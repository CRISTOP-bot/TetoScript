import unittest

from tetoscript.__main__ import TetoScriptError, run


class InterpreterTests(unittest.TestCase):
    def test_variable_and_log(self):
        self.assertEqual(run('teto nombre = "Teto"\ntetolog ("Hola " + nombre)'), ["Hola Teto"])

    def test_true_branch(self):
        code = 'teto n = 25\nTeto n == 25:\n    tetolog ("sí")\nelse:\n    tetolog ("no")'
        self.assertEqual(run(code), ["sí"])

    def test_else_branch(self):
        code = 'Teto 2 > 3:\n    tetolog ("sí")\nelse:\n    tetolog ("no")'
        self.assertEqual(run(code), ["no"])

    def test_unknown_variable_fails(self):
        with self.assertRaisesRegex(TetoScriptError, "variable no definida"):
            run("tetolog (fantasma)")

    def test_rejects_arbitrary_python(self):
        with self.assertRaises(TetoScriptError):
            run("tetolog (__import__(\"os\"))")


if __name__ == "__main__":
    unittest.main()
