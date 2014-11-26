import sublime, sublime_plugin
import re

from collections import namedtuple

BracketPosition = namedtuple("BracketPosition", "position opener")
BracketResult = namedtuple("BracketResult", "success start end")

# House keeping for the async beast
activeChecks = 0
dismissedChecks = 0

# scopeNames is used to avoid a weird memory leak with Sublime Text which occurs
# when calling view.scope_name within an async routine
scopeNames = []


class SelectionListener(sublime_plugin.EventListener):

  def on_modified(self, view):

    if view.settings().get("is_test", False):
      self.on_modified_async(view)

    global scopeNames
    scopeNames = [view.scope_name(i) for i in range(len(self.getBufferContent(view)))]


  def on_modified_async(self, view):
    global activeChecks, dismissedChecks

    if activeChecks > 0:
      dismissedChecks += 1
      return

    contentRegion = sublime.Region(0, view.size())
    bufferContent = self.getBufferContent(view)

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


  def getBufferContent(self, view):

    contentRegion = sublime.Region(0, view.size())
    return view.substr(contentRegion)



def getFirstBracketError(codeStr, view):
  global scopeNames

  opener = list("({[")
  closer = list(")}]")

  matchingStack = []

  for index, char in enumerate(codeStr):

    if dismissedChecks > 0:
      # we will have to start over
      return BracketResult(True, -1, -1)

    scopeName = scopeNames[index]

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
