Sublime BracketGuard [![Build Status](https://travis-ci.org/philippotto/Sublime-BracketGuard.svg?branch=master)](https://travis-ci.org/philippotto/Sublime-BracketGuard)
==============

A Sublime Text 2/3 Plugin which immediately highlights incorrect brackets.
Balancing different kinds of brackets is a requirement which can be found in a broad set of programming languages.
Nevertheless, Sublime Text does not highlight obviously wrong parenthesis.
BracketGuard changes this.

A quick test: Can you tell me, whether the following code is valid?

![](http://philippotto.github.io/Sublime-BracketGuard/screens/faulty_code.jpg)

I'm sure you can!
You don't even have to know the language to see that the brackets are wrong.
But how long did it take you to find the error?
And how long did it take you to realize that there are two brackets wrong instead of only one?

With the help of BracketGuard you will spot syntactic bracket mistakes in a split second.
Here is an example of how mistakes will be highlighted:

![](http://philippotto.github.io/Sublime-BracketGuard/screens/highlighted_code_2.jpg)

BracketGuard will highlight the first unexpected closing bracket and the corresponding opening bracket to which its counterpart is expected.
After finding the first bracket error, BracketGuard will stop to check the rest of your code, because following mistakes cannot be determined due to the corrupt balancing.

## Installation

Either use [Package Control](https://sublime.wbond.net/installation) and search for `BracketGuard` or clone this repository into the Sublime Text "Packages" directory.
