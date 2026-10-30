---
title: Accessibility Statement
linkTitle: Accessibility
description: Accessibility statement
# Voluntary statement - ansible-oracle is not obliged by BITV 2.0 or BFSG.
# Update "Known limitations" with the result of "task test:a11y".
layout: legal
---

We want this documentation to be usable by everyone,
including people using screen readers, keyboard navigation or magnification software.
This statement is voluntary.

## Target standard

We aim to conform to the
[Web Content Accessibility Guidelines (WCAG) 2.1](https://www.w3.org/TR/WCAG21/), level AA.

## Conformance status

This website is **partially accessible**.

## Known limitations

- Code blocks with a horizontal scroll bar cannot be reached with the keyboard.
- Diagrams in some guides have no detailed text description.

We are working on fixing these limitations.

## How is this tested?

Every page is tested automatically with [pa11y](https://pa11y.org/)
and [axe](https://github.com/dequelabs/axe-core) against WCAG 2 AA.
Automated tests find only some of the possible problems.
There has been no manual audit by accessibility experts.

## Report a barrier

If you encounter a barrier, please report it:

- via [GitHub Issues](https://github.com/oravirt/ansible-oracle/issues) or
- by e-mail to thorsten.bruhns at googlemail.com.

## Last updated

This statement was last updated on {{< lastmod >}}.
