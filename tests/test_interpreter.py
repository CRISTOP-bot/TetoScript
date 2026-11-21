import unittest
from tetoscript.lexer import TetoSyntaxError
from tetoscript.runtime import TetoRuntimeError, run

class InterpreterTests(unittest.TestCase):
    def test_example_functions_types_modulo_and_branches(self):
        source='''teto name: string = "Teto"
teto age: number = 25
teto fn greet(person: string) -> string { return "Hello " + person }
Teto (age % 2 == 1) { tetolog(greet(name)) } else { tetolog("nose") }'''
        self.assertEqual(run(source),["Hello Teto"])
    def test_else_branch_and_null_spelling(self):
        self.assertEqual(run('Teto (false) { tetolog("yes") } else { tetolog(nose) }'),["nose"])
    def test_type_annotation_rejects_wrong_type(self):
        with self.assertRaisesRegex(TetoRuntimeError,"se esperaba number"):
            run('teto age: number = "25"')
    def test_function_argument_type_is_checked(self):
        with self.assertRaisesRegex(TetoRuntimeError,"se esperaba string"):
            run('teto fn greet(name: string) -> string { return name } tetolog(greet(25))')
    def test_undefined_name_reports_error(self):
        with self.assertRaisesRegex(TetoRuntimeError,"variable no definida"):
            run('tetolog(ghost)')
    def test_rejects_unknown_character(self):
        with self.assertRaises(TetoSyntaxError): run('tetolog(@)')
    def test_rejects_duplicate_declaration(self):
        with self.assertRaisesRegex(TetoRuntimeError,"ya declarada"):
            run('teto x = 1 teto x = 2')
    def test_precedence_and_short_circuit(self):
        self.assertEqual(run('tetolog(2 + 3 * 4) tetolog(false and ghost)'),["14","false"])
    def test_non_callable_error(self):
        with self.assertRaisesRegex(TetoRuntimeError,"no se puede llamar"):
            run('teto x = 2 x()')

if __name__=="__main__": unittest.main()
