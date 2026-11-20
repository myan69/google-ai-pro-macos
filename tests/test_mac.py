import contextlib
import io
import types
import unittest
from unittest.mock import Mock, patch

import mac


class AdapterTests(unittest.TestCase):
    def test_multiple_devices_require_selection(self):
        listing = 'List of devices attached\none\tdevice\ntwo\tdevice\n'
        with patch.object(mac, 'adb_run', return_value=listing):
            with self.assertRaises(RuntimeError):
                mac.select_device('/adb')
            self.assertEqual(mac.select_device('/adb', 'two'), 'two')

    def test_console_summary_excludes_tokens_and_purchase_data(self):
        events = [
            {'ev': 'offer', 'id': 'trial', 'period': 'P1Y', 'micros': '0', 'token': 'PRIVATE_TOKEN'},
            {'ev': 'query_err', 'm': 'PRIVATE_ERROR_DETAIL'},
            {'ev': 'purchase_cb', 'purchase': 'PRIVATE_PAYMENT_DATA'},
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            mac.print_summary(events)
        text = output.getvalue()
        self.assertIn('trial', text)
        self.assertNotIn('PRIVATE_', text)

    def test_checkout_only_queries_and_detaches(self):
        upstream = Mock()
        upstream.build_js.return_value = 'local script'
        script = Mock()
        session = Mock()
        session.create_script.return_value = script
        device = Mock()
        device.attach.return_value = session
        fake_frida = types.SimpleNamespace(get_device=Mock(return_value=device))
        with patch.dict('sys.modules', {'frida': fake_frida}), patch.object(mac.time, 'sleep'):
            mac.query(upstream, 'chosen-device', 42, checkout=True, wait=0)
        fake_frida.get_device.assert_called_once_with('chosen-device', timeout=10)
        upstream.build_js.assert_called_once_with('pro12', list_only=False)
        upstream.process.assert_not_called()
        upstream.confirm_zero.assert_not_called()
        upstream.add_card.assert_not_called()
        upstream.add_account.assert_not_called()
        session.detach.assert_called_once()

    def test_listing_does_not_request_checkout(self):
        upstream = Mock()
        session = Mock()
        fake_frida = types.SimpleNamespace(get_device=Mock(return_value=Mock(attach=Mock(return_value=session))))
        with patch.dict('sys.modules', {'frida': fake_frida}), patch.object(mac.time, 'sleep'):
            mac.query(upstream, 'chosen-device', 42, checkout=False, wait=0)
        upstream.build_js.assert_called_once_with('pro12', list_only=True)

    def test_detach_on_script_failure(self):
        session = Mock()
        session.create_script.side_effect = RuntimeError('script error')
        fake_frida = types.SimpleNamespace(get_device=Mock(return_value=Mock(attach=Mock(return_value=session))))
        with patch.dict('sys.modules', {'frida': fake_frida}):
            with self.assertRaises(RuntimeError):
                mac.query(Mock(), 'chosen-device', 42)
        session.detach.assert_called_once()


if __name__ == '__main__':
    unittest.main()
