#!/usr/bin/env python3

import json, math, sys

class Product:
    def __init__(self, name, initial_price, revenue, price_increase_rate,
            output_quantity, input1_name, input1_quantity, input2_name,
            input2_quantity):
        self.name = name
        self.initial_price = initial_price
        self.revenue = revenue
        self.price_increase_rate = price_increase_rate
        self.output_quantity = output_quantity
        self.input1_name = input1_name
        self.input1_quantity = input1_quantity
        self.input2_name = input2_name
        self.input2_quantity = input2_quantity

class Rankable:
    def __init__(self, product, desired_rank):
        self.product = product
        self.desired_rank = desired_rank
        self.current_rank = 0

    def next_rank_cost(self):
        return math.ceil(
            self.product.initial_price * math.pow(
                1+self.product.price_increase_rate,
                self.current_rank
            )
        )

    def advance_rank(self):
        self.current_rank += 1

    def produce(self, inventories):
        produced_batches = self.current_rank
        if self.product.input1_quantity > 0:
            limit_by_input1 = int(inventories[self.product.input1_name] /
                self.product.input1_quantity)
            produced_batches = min(produced_batches, limit_by_input1)
        if self.product.input2_quantity > 0:
            limit_by_input2 = int(inventories[self.product.input2_name] /
                self.product.input2_quantity)
            produced_batches = min(produced_batches, limit_by_input2)
        # We now know how many we can produce, so subtract the appropriate
        # amount from the input inventories and add to the output inventory.
        input1_consumed = produced_batches * self.product.input1_quantity
        input2_consumed = produced_batches * self.product.input2_quantity
        output_produced = produced_batches * self.product.output_quantity
        if self.product.input1_quantity > 0:
            inventories[self.product.input1_name] -= input1_consumed
        if self.product.input2_quantity > 0:
            inventories[self.product.input2_name] -= input2_consumed
        inventories[self.product.name] += output_produced

    def sell_excess(self, inventories):
        excess = inventories[self.product.name]
        inventories[self.product.name] = 0
        inventories['money'] += excess * self.product.revenue

    def wants_more_ranks(self):
        return self.desired_rank > self.current_rank

class CraftingIdleClickerGame:
    def __init__(self, products, target_ranks):
        self.products = products
        self.rankables = []
        self.tick_count = 0
        # We always start a new game with 10 money.
        self.leftover_money = 10

        for product in self.products.values():
            target_rank = 0
            if product.name in target_ranks:
                target_rank = target_ranks[product.name]
            self.rankables.append(Rankable(product,target_rank))
        self.rankables.sort(key=lambda r: r.product.initial_price)

        self.fix_desired_ranks()

    def next_desired_rankable(self):
        lowest_cost_rank = float('inf')
        lowest_cost_rankable = None

        for rankable in self.rankables:
            if rankable.wants_more_ranks():
                next_rank_cost = rankable.next_rank_cost()
                if next_rank_cost < lowest_cost_rank:
                    lowest_cost_rank = next_rank_cost
                    lowest_cost_rankable = rankable

        return (lowest_cost_rankable, lowest_cost_rank)

    def fix_desired_ranks(self):
        """Adjusts ranks of all earlier products to provide enough input
        inventory for later products."""
        additional_ranks_needed = {}
        for rankable in reversed(self.rankables):
            # Check if later products need more of this product than we
            # currently desire.
            if rankable.product.name in additional_ranks_needed:
                rankable.desired_rank = max(rankable.desired_rank,
                    additional_ranks_needed[rankable.product.name])
                del additional_ranks_needed[rankable.product.name]

            # Ranks should always be a multiple of 10.
            rankable.desired_rank = 10 * math.ceil(rankable.desired_rank / 10)

            # Indicate how many we need of each of the inputs.
            if rankable.product.input1_quantity > 0:
                if rankable.product.input1_name not in additional_ranks_needed:
                    additional_ranks_needed[rankable.product.input1_name] = 0
                additional_ranks_needed[rankable.product.input1_name] += \
                    rankable.desired_rank * rankable.product.input1_quantity
            if rankable.product.input2_quantity > 0:
                if rankable.product.input2_name not in additional_ranks_needed:
                    additional_ranks_needed[rankable.product.input2_name] = 0
                additional_ranks_needed[rankable.product.input2_name] += \
                    rankable.desired_rank * rankable.product.input2_quantity

    def calc_profit_per_tick(self):
        inventories = {'money': 0}
        for product in self.products.values():
            inventories[product.name] = 0

        for rankable in self.rankables:
            rankable.produce(inventories)
        for rankable in self.rankables:
            rankable.sell_excess(inventories)

        return inventories['money']

    def run(self):
        next_rankable, next_rank_cost = self.next_desired_rankable()

        while next_rankable != None:
            if self.leftover_money >= next_rank_cost:
                # We're not going to advance ticks if we can purchase without
                # one. That way, we simulate the game's multi-purchase.
                self.leftover_money -= next_rank_cost
                next_rankable.advance_rank()
            else:
                # Calculate # of ticks until we can purchase the next rank.
                profit_per_tick = self.calc_profit_per_tick()
                remaining_cost = next_rank_cost - self.leftover_money
                ticks_to_purchase = math.ceil(remaining_cost / profit_per_tick)
                # Advance that many ticks.
                self.tick_count += ticks_to_purchase
                self.leftover_money += profit_per_tick * ticks_to_purchase
                # And purchase the rank.
                self.leftover_money -= next_rank_cost
                next_rankable.advance_rank()

            next_rankable, next_rank_cost = self.next_desired_rankable()

class CraftingIdleClickerDriver:
    def __init__(self, json_data_filename, json_target_quantities_filename):
        self.json_data_filename = json_data_filename
        self.json_target_quantities_filename = json_target_quantities_filename
        self.products = {}
        self.target_ranks = {}

    def read_product_data(self):
        with open(self.json_data_filename, 'r') as f:
            product_data_dicts = json.loads(f.read())
            self.products = {}
            for product_dict in product_data_dicts:
                self.products[product_dict['name']] = Product(**product_dict)

    def check_product_data(self):
        errors_encountered = False
        for product in self.products.values():
            if product.input1_quantity > 0 and \
                    self.products[product.input1_name].initial_price > \
                        product.initial_price:
                print("Error: product {} costs more than input {}".format(
                    product.name, product.input1_name))
                errors_encountered = True
            if product.input2_quantity > 0 and \
                    self.products[product.input2_name].initial_price > \
                        product.initial_price:
                print("Error: product {} costs more than input {}".format(
                    product.name, product.input2_name))
                errors_encountered = True
        if errors_encountered:
            print("Errors encountered in product data. Exiting.")
            sys.exit(1)

    def read_target_data(self):
        with open(self.json_target_quantities_filename) as f:
            self.target_ranks = json.loads(f.read())

    def run(self):
        self.read_product_data()
        self.check_product_data()
        self.read_target_data()
        game = CraftingIdleClickerGame(self.products,self.target_ranks)
        game.run()
        print("Ticks required: {}".format(game.tick_count))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: cic.py <json_product_data_filename>" + \
            " <json_target_quantities_filename>", file=sys.stderr)
        sys.exit(1)
    cic_driver = CraftingIdleClickerDriver(sys.argv[1], sys.argv[2])
    cic_driver.run()
