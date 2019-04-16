#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

for line in sys.stdin:
    for token in line.strip().split():
        if '▁' in token.strip('▁'):
            print(token)
