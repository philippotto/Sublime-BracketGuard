import sublime, sublime_plugin
import re

from collections import namedtuple

BracketPosition = namedtuple("BracketPosition", "position opener")
BracketResult = namedtuple("BracketResult", "success start end")

# House keeping for the async beast
activeChecks = 0
dismissedChecks = 0

class SelectionListener(sublime_plugin.EventListener):

  def on_modified(self, view):

    if view.settings().get("is_test", False):
      self.on_modified_async(view)


  def on_modified_async(self, view):

    global activeChecks, dismissedChecks

    if activeChecks > 0:
      dismissedChecks += 1
      return

    contentRegion = sublime.Region(0, view.size())
    bufferContent = view.substr(contentRegion)

    activeChecks += 1
    bracketResult = getFirstBracketError(bufferContent, view)
    if dismissedChecks > 0:
      dismissedChecks = 0
      bracketResult = getFirstBracketError(bufferContent, view)
    activeChecks -= 1

    if bracketResult.success:
      view.erase_regions("BracketGuardRegions")
    else:
      openerRegion = sublime.Region(bracketResult.start, bracketResult.start + 1)
      closerRegion = sublime.Region(bracketResult.end, bracketResult.end + 1)
      view.add_regions("BracketGuardRegions", [openerRegion, closerRegion], "invalid")



def getFirstBracketError(codeStr, view):

  opener = list("({[")
  closer = list(")}]")

  matchingStack = []

  for index, char in enumerate(codeStr):

    if dismissedChecks > 0:
      # we will have to start over
      return

    scopeName = view.scope_name(index)
    if "string" in scopeName or "comment" in scopeName:
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
    return BracketResult(True, -1, -1)
  else:
    poppedOpener = matchingStack.pop()
    return BracketResult(False, poppedOpener.position, len(codeStr) - 1)
