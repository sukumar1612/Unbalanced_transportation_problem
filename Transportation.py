import numpy as np

from NorthWestCornerMethod import NCWR


class Btransportation:
    @staticmethod
    def get_possible_next_nodes(loop, not_visited):
        last_node = loop[-1]
        nodes_in_row = [n for n in not_visited if n[0] == last_node[0]]
        nodes_in_column = [n for n in not_visited if n[1] == last_node[1]]
        if len(loop) < 2:
            return nodes_in_row + nodes_in_column
        else:
            prev_node = loop[-2]
            row_move = prev_node[0] == last_node[0]
            if row_move: return nodes_in_column
            return nodes_in_row

    @staticmethod
    def can_be_improved(ws):
        for p, v in ws:
            if v > 0: return True
        return False

    @staticmethod
    def get_entering_variable_position(ws):
        ws_copy = ws.copy()
        ws_copy.sort(key=lambda w: w[1])
        return ws_copy[-1][0]

    @staticmethod
    def get_us_and_vs(bfs, costs):
        us = [None] * len(costs)
        vs = [None] * len(costs[0])
        us[0] = 0
        bfs_copy = bfs.copy()
        while len(bfs_copy) > 0:
            for index, bv in enumerate(bfs_copy):
                i, j = bv[0]
                if us[i] is None and vs[j] is None: continue

                cost = costs[i][j]
                if us[i] is None:
                    us[i] = cost - vs[j]
                else:
                    vs[j] = cost - us[i]
                bfs_copy.pop(index)
                break

        return us, vs

    @staticmethod
    def get_ws(bfs, costs, us, vs):
        ws = []
        for i, row in enumerate(costs):
            for j, cost in enumerate(row):
                non_basic = all([p[0] != i or p[1] != j for p, v in bfs])
                if non_basic:
                    ws.append(((i, j), us[i] + vs[j] - cost))

        return ws

    @staticmethod
    def get_loop(bv_positions, ev_position):
        def inner(loop):
            if len(loop) > 3:
                can_be_closed = len(Btransportation.get_possible_next_nodes(loop, [ev_position])) == 1
                if can_be_closed: return loop

            not_visited = list(set(bv_positions) - set(loop))
            possible_next_nodes = Btransportation.get_possible_next_nodes(loop, not_visited)
            for next_node in possible_next_nodes:
                new_loop = inner(loop + [next_node])
                if new_loop: return new_loop

        return inner([ev_position])

    @staticmethod
    def loop_pivoting(bfs, loop):
        even_cells = loop[0::2]
        odd_cells = loop[1::2]
        get_bv = lambda pos: next(v for p, v in bfs if p == pos)
        leaving_position = sorted(odd_cells, key=get_bv)[0]
        leaving_value = get_bv(leaving_position)

        new_bfs = []
        for p, v in [bv for bv in bfs if bv[0] != leaving_position] + [(loop[0], 0)]:
            if p in even_cells:
                v += leaving_value
            elif p in odd_cells:
                v -= leaving_value
            new_bfs.append((p, v))

        return new_bfs

    @staticmethod
    def get_balanced_tp(supply, demand, costs, penalties=None):
        total_supply = sum(supply)
        total_demand = sum(demand)

        if total_supply < total_demand:
            if penalties is None:
                raise Exception('Supply less than demand, penalties required')
            new_supply = supply + [total_demand - total_supply]
            new_costs = costs + [penalties]
            return new_supply, demand, new_costs
        if total_supply > total_demand:
            new_demand = demand + [total_supply - total_demand]
            new_costs = costs + [[0 for _ in demand]]
            return supply, new_demand, new_costs
        return supply, demand, costs

    @staticmethod
    def transportation_simplex_method(supply, demand, costs, penalties=None):
        balanced_supply, balanced_demand, balanced_costs = Btransportation.get_balanced_tp(
            supply, demand, costs
        )

        def inner(bfs):
            us, vs = Btransportation.get_us_and_vs(bfs, balanced_costs)
            ws = Btransportation.get_ws(bfs, balanced_costs, us, vs)
            if Btransportation.can_be_improved(ws):
                ev_position = Btransportation.get_entering_variable_position(ws)
                loop = Btransportation.get_loop([p for p, v in bfs], ev_position)
                return inner(Btransportation.loop_pivoting(bfs, loop))
            return bfs

        basic_variables = inner(NCWR.north_west_corner(balanced_supply, balanced_demand))
        solution = np.zeros((len(costs), len(costs[0])))
        for (i, j), v in basic_variables:
            solution[i][j] = v

        return solution

    @staticmethod
    def get_total_cost(costs, solution):
        total_cost = 0
        for i, row in enumerate(costs):
            for j, cost in enumerate(row):
                total_cost += cost * solution[i][j]
        return total_cost


class UBtransportation:
    @staticmethod
    def convert_ub_transportation_to_b(costs, supply, demand):
        supsum = sum(supply)
        demandsum = sum(demand)
        if supsum == demandsum:
            return
        elif supsum > demandsum:
            demand.append(supsum - demandsum)
            for i in range(0, len(costs)):
                costs[i].append(0)
        else:
            supply.append(demandsum - supsum)
            costs.append([i for i in range(0, len(demand))])
        return
