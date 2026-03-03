import unittest
from unittest.mock import patch, mock_open, MagicMock

from core.crypto import RSACryptoSystem
from core.i18n import t, T
from core.config_parser import load_config, get_lab_config
from core.session_manager import reset_lab_state


class TestCoreCrypto(unittest.TestCase):
    """Tests for the cryptographic primitives."""

    def setUp(self):
        # Using a smaller key size (1024) specifically for faster unit tests
        self.crypto = RSACryptoSystem(key_size=1024)

    def test_sign_and_verify(self):
        message = b"confidential vote data"
        signature = self.crypto.sign(message)
        
        self.assertTrue(RSACryptoSystem.verify(self.crypto.public_key, message, signature))
        self.assertFalse(RSACryptoSystem.verify(self.crypto.public_key, b"tampered data", signature))

    def test_hybrid_encrypt_and_decrypt(self):
        message = b"secret ballot"
        ciphertext = RSACryptoSystem.encrypt(self.crypto.public_key, message)
        decrypted_message = self.crypto.decrypt(ciphertext)
        
        self.assertEqual(message, decrypted_message)

    def test_raw_homomorphic_operations(self):
        params = self.crypto.get_key_parameters()
        n, e = params["n"], params["e"]
        
        original_int = 42
        encrypted_int = RSACryptoSystem.raw_encrypt(n, e, original_int)
        decrypted_int = self.crypto.raw_decrypt(encrypted_int)
        
        self.assertEqual(original_int, decrypted_int)


class TestCoreI18n(unittest.TestCase):
    """Tests for the internationalization module."""

    def test_translation_existing_key(self):
        self.assertEqual(t(T.APP_TITLE, "English"), "Simulation:")

    def test_translation_fallback(self):
        # Should return the key itself if not found
        self.assertEqual(t("NON_EXISTENT_KEY", "English"), "NON_EXISTENT_KEY")

    def test_translation_with_kwargs(self):
        # Format string: "Voter {voter} is preparing ballot for {candidate}..."
        result = t(T.VOTER_PREPARING, "English", voter="John", candidate="Alice")
        self.assertIn("John", result)
        self.assertIn("Alice", result)


class TestCoreConfigParser(unittest.TestCase):
    """Tests for the YAML configuration parser."""

    @patch("core.config_parser.Path.is_file", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="labs:\n  - id: 1\n    protocol: simple")
    def test_load_config_success(self, mock_file, mock_is_file):
        config = load_config("dummy_path.yaml")
        self.assertIn("labs", config)
        self.assertEqual(config["labs"][0]["id"], 1)

    @patch("core.config_parser.Path.is_file", return_value=False)
    def test_load_config_file_not_found(self, mock_is_file):
        with self.assertRaises(FileNotFoundError):
            load_config("missing.yaml")

    def test_get_lab_config_success(self):
        dummy_config = {"labs": [{"id": 1, "protocol": "simple"}, {"id": 2, "protocol": "blind"}]}
        lab_cfg = get_lab_config(dummy_config, 2)
        self.assertEqual(lab_cfg["protocol"], "blind")

    def test_get_lab_config_not_found(self):
        dummy_config = {"labs": [{"id": 1}]}
        with self.assertRaises(ValueError):
            get_lab_config(dummy_config, 99)


class TestCoreSessionManager(unittest.TestCase):
    """Tests for the Streamlit session state manager."""

    def setUp(self):
        """Setup reusable mock session state and dummy configs."""
        self.patcher = patch("core.session_manager.st")
        self.mock_st = self.patcher.start()
        self.mock_st.session_state = MagicMock()
        self.mock_st.session_state.logs = []
        
        self.base_config = {
            "settings": {
                "candidates": ["Candidate A", "Candidate B"], 
                "num_voters": 2,
                "candidate_ids": {"Candidate A": 24, "Candidate B": 12}
            }
        }

    def tearDown(self):
        """Stop the patcher after each test."""
        self.patcher.stop()

    def test_reset_lab_state_simple_protocol(self):
        config = {**self.base_config, "protocol": "simple"}
        reset_lab_state(config, "lab1", "English")
        
        self.assertEqual(self.mock_st.session_state.lab_id, "lab1")
        self.assertIsNotNone(self.mock_st.session_state.cvk)
        self.assertEqual(len(self.mock_st.session_state.voters), 2)

    def test_reset_lab_state_blind_protocol(self):
        config = {**self.base_config, "protocol": "blind"}
        reset_lab_state(config, "lab2", "English")
        
        self.assertEqual(self.mock_st.session_state.lab_id, "lab2")
        self.assertIsNotNone(self.mock_st.session_state.cvk)

    def test_reset_lab_state_split_protocol(self):
        config = {**self.base_config, "protocol": "split"}
        reset_lab_state(config, "lab3", "English")
        
        self.assertIsNotNone(self.mock_st.session_state.br)
        self.assertIsNotNone(self.mock_st.session_state.cvk)

    def test_reset_lab_state_factor_protocol(self):
        config = {**self.base_config, "protocol": "factor"}
        reset_lab_state(config, "lab4", "English")
        
        self.assertIsNotNone(self.mock_st.session_state.vc1)
        self.assertIsNotNone(self.mock_st.session_state.vc2)
        self.assertIsNotNone(self.mock_st.session_state.cvk)

    def test_reset_lab_state_decentralized_protocol(self):
        config = {**self.base_config, "protocol": "decentralized"}
        reset_lab_state(config, "lab5", "English")
        
        self.assertIsNotNone(self.mock_st.session_state.cvk)

    def test_reset_lab_state_lab6_advanced_protocol(self):
        config = {**self.base_config, "protocol": "lab6_advanced"}
        reset_lab_state(config, "lab6", "English")
        
        self.assertIsNotNone(self.mock_st.session_state.rb)
        self.assertEqual(len(self.mock_st.session_state.mcs), 2)
        self.assertEqual(len(self.mock_st.session_state.lcs), 4)
        self.assertIsNotNone(self.mock_st.session_state.cvk)


if __name__ == '__main__':
    unittest.main()