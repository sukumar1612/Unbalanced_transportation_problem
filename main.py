from Transportation import Btransportation, UBtransportation


if __name__ == '__main__':
    costs = [
        [11, 20, 7, 8],
        [21, 16, 10, 12],
        [8, 12, 18, 9]
    ]
    supply = [50, 40, 70]
    demand = [30, 25, 35, 40]
    UBtransportation.convert_ub_transportation_to_b(costs, supply, demand)

    solution = Btransportation.transportation_simplex_method(supply, demand, costs)
    print('total cost: ', Btransportation.get_total_cost(costs, solution))