import sublime
from unittest import TestCase

version = sublime.version()

class TestBracketGuard(TestCase):

	def setUp(self):

		self.view = sublime.active_window().new_file()
		self.view.settings().set("is_test", True)


	def tearDown(self):

		if self.view:
			self.view.set_scratch(True)
			self.view.window().run_command("close_file")


	def insertCodeAndGetRegions(self, code):

		self.view.run_command("insert", {"characters": code})
		return self.view.get_regions("BracketGuardRegions")


	def testPureValidBrackets(self):

		openerRegions = self.insertCodeAndGetRegions("([{}])")
		self.assertEqual(len(openerRegions), 0)


	def testValidBracketsInCode(self):

		openerRegions = self.insertCodeAndGetRegions("a(bc[defg{hijkl}mn])o")
		self.assertEqual(len(openerRegions), 0)


	def testInvalidBracketsWrongCloser(self):

		bracketGuardRegions = self.insertCodeAndGetRegions("({}])")

		self.assertEqual(len(bracketGuardRegions), 2)
		self.assertEqual(bracketGuardRegions[0].a, 0)
		self.assertEqual(bracketGuardRegions[1].a, 3)


	def testInvalidBracketsNoCloser(self):

		bracketGuardRegions = self.insertCodeAndGetRegions("({}")

		self.assertEqual(len(bracketGuardRegions), 2)
		self.assertEqual(bracketGuardRegions[0].a, -1)
		self.assertEqual(bracketGuardRegions[1].a, 0)


	def testInvalidBracketsNoOpener(self):

		bracketGuardRegions = self.insertCodeAndGetRegions("){}")

		self.assertEqual(len(bracketGuardRegions), 2)
		self.assertEqual(bracketGuardRegions[0].a, -1)
		self.assertEqual(bracketGuardRegions[1].a, 0)
