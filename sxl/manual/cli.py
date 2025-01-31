HELP_MANIFOLD = """manifold

Synopsis\tConfigure the manifold.

Aliases\t\tmf

Subcommands\tmanifold create <metric>
\t\tmanifold define <geometrical object>
\t\tmanifold recreate <new metric>
\t\tmanifold reload"""

HELP_MANIFOLD_CREATE = """manifold create

Synopsis\tCreate a new manifold with a given metric.

Aliases\t\tmf create
\t\tmf c

Syntax\t\tmanifold create <metric name/search terms>

Description\tRun this before any simulations begin to create a new manifold. Search terms will use the built-in
\t\tlibrary to find a result. For example, searching "schwarzschild" is specific enough and will
\t\tautomatically find the schwarzschild metric;

\t\t\tmanifold create schwarzschild

\t\tAdditionally, if the search terms are not specific enough, clarification will be requested;
\t\tthe top 36 results will be displayed and the number/letter keys can be used to select one.
\t\tFor example:

\t\t\tmanifold create vac

\t\t\tPlease clarify:
\t\t\t        1       Schwarzschild metric
\t\t\t        2       spherical Minkowski metric
\t\t\t        3       cylindrical Minkowksi metric
\t\t\t        4       rectangular Minkowski metric

\t\tThe results are also sorted from highest relevance to least relevance, so a safe bet in this
\t\tcase is to just press 1 to select the most relevant result. See the documentation for the
\t\tsxl.library submodule for more information on how the searching system works.
"""

HELP_MANIFOLD_DEFINE = """manifold define

Synopsis\tDefine a new scalar/vector/tensor field on the manifold

Aliases\t\tmf define
\t\tmf d

Syntax\t\tmanifold define <object name/search terms>

Description\tRuns the definition and computation of a new geometrical object (scalar/vector/tensor) on the
\t\tmanifold. Some options can define multiple objects (for example,

\t\t\tmanifold define everything

\t\twill define everything in the standard library necessary for the solution of the Einstein
\t\tfield equations.)

\t\tAdditionally, if the search terms are not specific enough, clarification will be requested;
\t\tthe top 36 results will be displayed and the number/letter keys can be used to select one.
\t\tFor example:

\t\t\tmanifold create vac

\t\t\tPlease clarify:
\t\t\t        1       Schwarzschild metric
\t\t\t        2       spherical Minkowski metric
\t\t\t        3       cylindrical Minkowksi metric
\t\t\t        4       rectangular Minkowski metric

\t\tThe results are also sorted from highest relevance to least relevance, so a safe bet in this
\t\tcase is to just press 1 to select the most relevant result. See the documentation for the
\t\tsxl.library submodule for more information on how the searching system works.
"""

HELP_MANIFOLD_REPORT = """manifold report

Synopsis\tTake a mathematical look at something.

Aliases\t\tmf report
\t\tmf r

Syntax\t\tmanifold report <object name/search terms> [-i/--indices <indices, if applicable>] [--co/--contra/--mixed, if applicable] [-a/--auto]

Description\tSearches for the specified object. If it's defined on the manifold, it'll pull up manifold.of(object)
and use Sympy's pretty-printer to display the value/component referred to, and if the object
doesn't already exist, the command will indicate that. 

Indices are specified after the -i flag, when applicable, and can be either number or letters, 
with numbers being able to be blocked into one word and letters requiring being split up into 
multiple words. For example, in (t, x, y, z) coordinates, these index arguments are identical
in function,

\t\t\t... -i 0123
\t\t\t... -i t x y z
\t\t\t... -i t 1 y 3

but the first is preferred over the other two.

For example, to get the timelike component of the stress-energy-momentum tensor (energy density),
the command would be

\t\t\tmanifold report stress-energy-momentum tensor -i 00

and the result of that search would be subsequently pretty-printed.

If you pass the -a/--auto flag (AFTER indices - it must be the last word of the command), then
if the search reveals that the requested object does not exist on the manifold/hasn't been defined
yet, then SXL will automatically define, compute, and print it. Otherwise, no results will be
returned.
"""