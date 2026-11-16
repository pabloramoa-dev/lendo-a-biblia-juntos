import unittest
import argparse
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from tools.rotina import periodo_da_execucao, selecionar, validar_item, confirmar
from tools.montar_item import montar, plano


class RotinaTests(unittest.TestCase):
    def test_todos_os_730_episodios_tem_leitura_e_comentario(self):
        self.assertEqual(len(plano()), 730)
        for eid in plano():
            with self.subTest(episodio=eid):
                validar_item(montar(eid))

    def test_primeiros_de_cada_periodo(self):
        eps = list(plano().values())
        self.assertEqual(selecionar(eps, [], "manha", "2026-11-16")["id"], "M001")
        self.assertEqual(selecionar(eps, [], "noite", "2026-11-16")["id"], "N001")

    def test_reexecucao_no_mesmo_turno_nao_duplica(self):
        registro = {"id": "M001", "periodo": "manha", "data_brt": "2026-11-16"}
        self.assertIsNone(selecionar(list(plano().values()), [registro], "manha", "2026-11-16"))

    def test_outro_turno_do_mesmo_dia_continua_disponivel(self):
        registro = {"id": "M001", "periodo": "manha", "data_brt": "2026-11-16"}
        self.assertEqual(selecionar(list(plano().values()), [registro], "noite", "2026-11-16")["id"], "N001")

    def test_interrupcao_nao_pula_episodio(self):
        registro = {"id": "M001", "periodo": "manha", "data_brt": "2026-11-16"}
        self.assertEqual(selecionar(list(plano().values()), [registro], "manha", "2026-11-20")["id"], "M002")

    def test_atraso_do_runner_nao_troca_turno(self):
        tarde = datetime(2026, 11, 16, 23, tzinfo=timezone.utc)
        self.assertEqual(periodo_da_execucao("automatico", "0 9 * * *", tarde), "manha")
        self.assertEqual(periodo_da_execucao("automatico", "0 21 * * *", tarde), "noite")

    def test_horario_manual_e_brasilia(self):
        self.assertEqual(periodo_da_execucao("automatico", "", datetime(2026, 11, 16, 13, tzinfo=timezone.utc)), "manha")
        self.assertEqual(periodo_da_execucao("automatico", "", datetime(2026, 11, 16, 22, tzinfo=timezone.utc)), "noite")

    def test_final_do_plano_nao_recicla_episodios(self):
        eps = list(plano().values())
        registros = [{"id": e["id"], "periodo": e["periodo"], "data_brt": "2026-01-01"} for e in eps]
        self.assertIsNone(selecionar(eps, registros, "manha", "2027-11-16"))

    def test_sem_upload_nao_avanca_historico(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'entrega').mkdir()
            (base / 'entrega/episodio.json').write_text(json.dumps({'modo': 'rotina'}))
            hist = base / 'historico.json'
            hist.write_text('{"registros": []}')
            with patch('tools.rotina.TRABALHO', base), patch('tools.rotina.HISTORICO', hist):
                with self.assertRaises(ValueError):
                    confirmar(argparse.Namespace(artifact_url='', artifact_id=''))
            self.assertEqual(json.loads(hist.read_text())['registros'], [])

    def test_confirmacao_idempotente_e_hash_conferido(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'entrega').mkdir()
            video = base / 'entrega/M001.mp4'
            video.write_bytes(b'bytes-do-video-validado')
            meta = {'id': 'M001', 'modo': 'rotina', 'periodo': 'manha', 'data_brt': '2026-11-16',
                    'sha256': hashlib.sha256(video.read_bytes()).hexdigest()}
            (base / 'entrega/episodio.json').write_text(json.dumps(meta))
            hist = base / 'historico.json'
            hist.write_text('{"registros": []}')
            with patch('tools.rotina.TRABALHO', base), patch('tools.rotina.HISTORICO', hist):
                args = argparse.Namespace(artifact_url='https://github.com/example/artifacts/1', artifact_id='1')
                confirmar(args)
                confirmar(args)
                self.assertEqual(len(json.loads(hist.read_text())['registros']), 1)
                video.write_bytes(b'video-alterado')
                with self.assertRaises(ValueError):
                    confirmar(args)

    def test_piloto_nao_consume_sequencia(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'entrega').mkdir()
            (base / 'entrega/episodio.json').write_text(json.dumps({'modo': 'piloto'}))
            with patch('tools.rotina.TRABALHO', base), patch('tools.rotina.HISTORICO', base / 'nao-existe.json'):
                confirmar(argparse.Namespace(artifact_url='', artifact_id=''))
            self.assertFalse((base / 'nao-existe.json').exists())


if __name__ == "__main__":
    unittest.main()
