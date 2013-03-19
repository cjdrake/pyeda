.. overview.rst

********
Overview
********

What is Electronic Design Eutomation (EDA)?
===========================================

The Intel 4004, the world's first commercially available microprocessor,
was built from approximately 2300 transistors,
and had a clock frequency of 740 kilohertz (thousands of cycles per second).
A modern Intel microprocessor can contain over 1.5 billion transistors,
and will typically have a clock frequency ranging from two to four gigahertz
(billions of cycles per second).

In 1971 it took less than one hundred people to manufacture the 4004.
That is approximately 23 transistors per employee.
If that ratio stayed the same between 1971 and 2012,
Intel would need to employ about 65 *million* people just to
produce the latest Core i7 processor.
That is **one fifth** the entire population of the United States!

Clearly, companies that design and manufacture integrated circuits have found
ways to be more productive since then.

Simply stated,
electronic design automation (EDA) is the science of optimizing productivity in
the design and manufacture of electronic components.

Goals
=====

After reading the previous section, EDA sounds like a vast field.
The way we have defined it covers everything from controlling robotic arms in
the fabrication plant to providing free coffee to keep interns busy.
We need to narrow our focus a bit.

PyEDA is primarily concerned with implementing the data structures and
algorithms necessary for performing logic synthesis and verification.
These tools form the theoretical foundation for the implementation of CAD tools
for designing VLSI (Very Large Scale Integrated circuit).

PyEDA is a hobby project,
and is very unlikely to ever be a competitor to state-of-the-art EDA industry
technology.
It should be useful for academic exploration and experimentation.
If you use PyEDA, please email the author with your success/failure stories.

Free Software
=============

PyEDA is free software; you can use it or redistribute it under the terms of
the "two-clause" BSD License.

Repository
==========

The PyEDA source code may be viewed on
`GitHub <http://github.com/cjdrake/pyeda>`_.
