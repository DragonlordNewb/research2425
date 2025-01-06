HELP_MANIFOLD = """manifold

Synopsis\tConfigure the manifold.

Subcommands\tmanifold create <metric>
\t\tmanifold define <geometrical object>
\t\tmanifold recreate <new metric>
\t\tmanifold reload"""

HELP_MANIFOLD_CREATE = """manifold create

Synopsis\tCreate a new manifold with a given metric.

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