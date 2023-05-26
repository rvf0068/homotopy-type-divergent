"""
Checks the homotopy type of the iterated graphs of some clique divergent graphs
"""
import argparse
import networkx as nx
import mogutda

from pycliques.simplicial import clique_complex
from pycliques.dominated import completely_pared_graph as p
from pycliques.dominated import complete_s_collapse, complete_s_collapse_edges
from pycliques.cliques import clique_graph as k
from pycliques.named import suspension_of_cycle


def simplify_ht(graph):
    """Simplifies the graph for homotopy type purposes"""
    v_graph = complete_s_collapse(graph)
    ev_graph = complete_s_collapse_edges(v_graph)
    vev_graph = complete_s_collapse(ev_graph)
    return vev_graph


def _read_dong(dong):
    """Converts the set given by dong_matching into a TeX string"""
    n_critical = len(dong)
    if n_critical == 0:
        return (True, "Contractible")
    else:
        list_dong = list(dong)
        dimension = len(list_dong[0])
        if n_critical == 1:
            return (True, f"\\(S^{ {dimension-1} }\\)")
        else:
            for simp in list_dong:
                if len(simp) != dimension:
                    return (False, dong)
            return (True, f"\\(\\vee_{ {n_critical} }S^{ {dimension-1} }\\)")


def homotopy_type(graph):
    """Attempts to get a homotopy type using Dong's matching"""
    c_complex = clique_complex(graph)
    dong1 = c_complex.dong_matching()
    if _read_dong(dong1)[0]:
        return _read_dong(dong1)[1]
    else:
        c_complex = clique_complex(simplify_ht(graph))
        dong2 = c_complex.dong_matching()
        if _read_dong(dong2)[0]:
            return _read_dong(dong2)[1]
        else:
            return (dong1, dong2)


def dimension_sc(complex):
    dims = [len(f) for f in complex.face_set]
    dims.sort()
    return dims[-1] - 1


# números de betti del complejo de completas de una gráfica
def betti_numbers(graph):
    def simplify_list(bettis):
        simplified = bettis
        while len(simplified) > 0 and simplified[-1] == 0:
            del simplified[-1]
        return simplified
    the_simplices = [tuple(c) for c in nx.find_cliques(graph)]
    the_complex = mogutda.SimplicialComplex(simplices=the_simplices)
    dim = dimension_sc(the_complex)
    numbers = [the_complex.betti_number(i) for i in range(dim+1)]
    numbers[0] = numbers[0] - 1  # reduced betti number
    return simplify_list(numbers)


def main():
    """Main function"""
    graph = suspension_of_cycle(args.index)
    results = f"ht_{args.index}.org"
    with open(results, 'a', encoding="utf8") as the_file:
        the_file.write("| index | order | HT |\n")
        iter = 0
        while graph is not None:
            if graph.order() < 50:
                h_t = homotopy_type(graph)
            else:
                h_t = betti_numbers(graph)
            the_file.write(f"|{iter}|{graph.order}|{h_t}|\n")
            graph = k(graph, args.bd)
            if graph is not None:
                graph = p(graph)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("index", type=int, help="Index of suspension")
    parser.add_argument("--bd", type=int, help="Upper bound", default=100)
    args = parser.parse_args()
    main()
