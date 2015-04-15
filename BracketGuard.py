import sublime, sublime_plugin
import re, time

from collections import namedtuple

BracketPosition = namedtuple("BracketPosition", "position opener")
BracketResult = namedtuple("BracketResult", "success start end")

bracketGuardRegions = "BracketGuardRegions"

class EventListener(sublime_plugin.EventListener):

  def __init__(self):

    self.latest_keypresses = {}


  def on_modified(self, view):

    if view.settings().get("is_test", False):
      self.highlightBracketError(view)


  def on_modified_async(self, view):

    self.clearRegions(view)
    if self.doAutoCheck(view):
       self.debounce(view, "modified", self.highlightBracketError)

  def on_post_save_async(self, view):

    if self.checkOnSave() and not self.doAutoCheck(view):
      self.highlightBracketError(view)


  def clearRegions(self, view):

    view.erase_regions(bracketGuardRegions)


  def settings(self):

    return sublime.load_settings("BracketGuard.sublime-settings")


  def checkOnSave(self):

    return self.settings().get("check_on_save")


  def doAutoCheck(self, view):

    threshold = self.settings().get("file_length_threshold")
    return threshold == -1 or threshold >= view.size()


  def highlightBracketError(self, view):

    bracketResult = self.getFirstBracketError(view)

    if not bracketResult.success:
      openerRegion = sublime.Region(bracketResult.start, bracketResult.start + 1)
      closerRegion = sublime.Region(bracketResult.end, bracketResult.end + 1)
      view.add_regions(bracketGuardRegions, [openerRegion, closerRegion], "invalid")


  def debounce(self, view, event_type, func):

    key = (event_type, view.file_name())
    this_keypress = time.time()
    self.latest_keypresses[key] = this_keypress
    debounceTime = self.settings().get("debounce_time", 500)

    def callback():
        latest_keypress = self.latest_keypresses.get(key, None)
        if this_keypress == latest_keypress:
            func(view)

    sublime.set_timeout_async(callback, debounceTime)


  def getFirstBracketError(self, view):

    opener = list("({[")
    closer = list(")}]")

    matchingStack = []
    successResult = BracketResult(True, -1, -1)
    codeStr = view.substr(sublime.Region(0, view.size()))

    for index, char in enumerate(codeStr):

      # this leaks memory ?
      # if len(codeStr) != view.size():
      #   return successResult

      if char not in opener and not char in closer:
        continue

      scopeName = view.scope_name(index)
      hasScope = lambda s: s in scopeName

      # workaround for the following code in markdown: ![example](img/example.png)
      markdownBracketScope = "punctuation.definition.string.begin.markdown"

      if hasScope("string") and not hasScope(markdownBracketScope) or hasScope("comment"):
        # ignore unmatched brackets in strings and comments
        continue

      if char in opener:
        matchingStack.append(BracketPosition(index, char))
      elif char in closer:
        matchingOpener = opener[closer.index(char)]

        if len(matchingStack) == 0:
          return BracketResult(False, -1, index)

        poppedOpener = matchingStack.pop()
        if matchingOpener != poppedOpener.opener:
          return BracketResult(False, poppedOpener.position, index)


    if len(matchingStack) == 0:
      return successResult
    else:
      poppedOpener = matchingStack.pop()
      return BracketResult(False, poppedOpener.position, -1)
