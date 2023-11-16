import logging

import mock

from odoo.tests.common import SavepointCase

logger = logging.getLogger(__name__)

class objet_mock():
    def __init__(self, state):
        self.istate = state

    def state(self):
        return self.istate
class TestAccountStatementImportSFTP(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Load test data."""
        super().setUpClass()
        cls.backend = cls._get_backend()
        cls.record = cls.backend.create_record("test_so_import", {})

    def test_failed_no_action(self):
        mock_create = mock.patch.object(
            type(self.env['account.statement.import']),
            'create',
        )
        mock_action = mock.patch.object(
            type(self.env['account.statement.import']),
            "import_file_button"
        )
        mock_statement = mock.patch.object(
            type(self.env["account.bank.statement"]),
            "browse"
        )
        mock_action.return_value = False
        mock_statement.return_value = objet_mock("posted")
        backend = self.backend._get_component(self.record, "process")
        with mock_create, mock_action, mock_statement:
            backend.process()
            self.assertRaises(ValueError, backend.process())

    def test_failed_state_open(self):
        mock_create = mock.patch.object(
            type(self.env['account.statement.import']),
            'create',
        )
        mock_action = mock.patch.object(
            type(self.env['account.statement.import']),
            "import_file_button"
        )
        mock_statement = mock.patch.object(
            type(self.env["account.bank.statement"]),
            "browse"
        )
        mock_action.return_value = True
        mock_statement.return_value = objet_mock("posted")
        backend = self.backend._get_component(self.record, "process")
        with mock_create, mock_action, mock_statement:
            backend.process()
            self.assertRaises(ValueError, backend.process())

    def test_sftp(self):
        mock_create = mock.patch.object(
            type(self.env['account.statement.import']),
            'create',
        )
        mock_action = mock.patch.object(
            type(self.env['account.statement.import']),
            "import_file_button"
        )
        mock_statement = mock.patch.object(
            type(self.env["account.bank.statement"]),
            "browse"
        )
        mock_action.return_value = True
        mock_statement.return_value = objet_mock("done")
        backend = self.backend._get_component(self.record, "process")
        with mock_create, mock_action, mock_statement:
            backend.process()
            mock_create.assert_called()
            mock_action.assert_called()
            mock_statement.assert_called()

    @classmethod
    def _get_backend(cls):
        return cls.env.ref("account_statement_import_sftp.demo_edi_backend_sftp")

    @classmethod
    def _create_exchange_type(cls, **kw):
        model = cls.env["edi.exchange.type"]
        vals = {
            "name": "Test CSV exchange",
            "backend_id": cls.backend.id,
            "backend_type_id": cls.backend.backend_type_id.id,
        }
        vals.update(kw)
        return model.create(vals)
