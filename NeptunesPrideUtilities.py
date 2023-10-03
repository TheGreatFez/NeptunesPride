import json
import requests
from GeneticAlgorithm import Organism, DNA

class NeptunesPrideData():
    root = "https://np.ironhelmet.com/api"
    game_id = 6113070671462400
    api_version = "0.1"

    def __init__(self, api_key: str, game_id: int) -> None:
        self.api_key: str = api_key
        self.game_id: int = game_id
        params = {
            "game_number" : self.game_id,
            "code" : self.api_key,
            "api_version" : self.api_version
        }
        self.game_data: dict = requests.post(self.root, params).json()

        with open("ScanningData.json", "w") as file:
            file.write(json.dumps(self.game_data, indent=4, sort_keys=True))

class CostScalars():
    Economy = 1
    Industry = 2
    Science = 8
    Warp_Gate = 20

class Star():

    def __init__(self, star_data: dict) -> None:
        self.name: str = star_data["n"]
        self.resources: int = star_data["nr"]
        self.economy: int = star_data["e"]
        self.industry: int = star_data["i"]
        self.science: int = star_data["s"]
        self.warp_gate: bool = star_data["ga"]
        self.economy_cost: int = None
        self.industry_cost: int = None
        self.science_cost: int = None

    def cost_equation(self, cost_scalar: CostScalars, terraforming_delta: int, current_level: int) -> int:
        return int(cost_scalar * (current_level + 1) * (500/(self.resources + terraforming_delta)))

    def set_cost_economy(self, terraforming_delta: int) -> int:
        self.economy_cost = self.cost_equation(CostScalars.Economy, terraforming_delta, self.economy)
    
    def buy_economy(self, terraforming_delta):
        self.economy += 1
        self.economy_cost = self.cost_equation(CostScalars.Economy, terraforming_delta, self.economy)
    
    def set_cost_industry(self, terraforming_delta: int) -> int:
        self.industry_cost =  self.cost_equation(CostScalars.Industry, terraforming_delta, self.industry)
    
    def buy_industry(self, terraforming_delta):
        self.industry += 1
        self.industry_cost = self.cost_equation(CostScalars.Industry, terraforming_delta, self.industry)
    
    def set_cost_science(self, terraforming_delta: int) -> int:
        self.science_cost = self.cost_equation(CostScalars.Science, terraforming_delta, self.science)
    
    def buy_science(self, terraforming_delta):
        self.science += 1
        self.science_cost = self.cost_equation(CostScalars.Science, terraforming_delta, self.science)    


class Research():
    def __init__(self, research_dict: dict) -> None:
        self.base_level_cost: int = research_dict["brr"]
        self.can_research: bool = self.base_level_cost == 0
        self.level: int = research_dict["level"]
        self.progress: int = research_dict["research"]
        self.next_level_cost: int = self.level*self.base_level_cost

class Tech():
    def __init__(self, tech_dict: dict) -> None:
        self.Scanning: Research = Research(tech_dict["scanning"])
        self.Hyperspace_Range: Research = Research(tech_dict["propulsion"])
        self.Terraforming: Research = Research(tech_dict["terraforming"])
        self.Weapons: Research = Research(tech_dict["weapons"])
        self.Banking: Research = Research(tech_dict["banking"])
        self.Manufacturing: Research = Research(tech_dict["manufacturing"])

    def get_industry_rate(self) -> int:
        return self.Manufacturing.level + 5
    
    def get_terraforming_delta(self) -> int:
        return self.Terraforming.level*5
    
    def get_banking_income(self) -> int:
        return self.Banking.level*75


class Player(Organism):

    def __init__(self, dna: DNA, name: str, game_data: dict) -> None:
        super().__init__(dna)
        self.name: str = name
        self.raw_game_data: dict = game_data
        self.reset_player()

    def __get_player_data(self, game_data: dict) -> dict:
        players_data = game_data["scanning_data"]["players"]

        for player_id in players_data:
            player = players_data[player_id]
            if player["alias"] == self.name:
                return player
        
        raise Exception(f"No player found by the name of {self.name}")
    
    def __get_player_owned_stars_data(self, game_data: dict) -> dict:
        owned_stars = []
        for star_id in game_data["scanning_data"]["stars"]:
            star_data = game_data["scanning_data"]["stars"][star_id]
            if star_data["puid"] == self.uid:
                owned_star = Star(star_data)
                owned_star.set_cost_economy(self.tech.get_terraforming_delta())
                owned_star.set_cost_industry(self.tech.get_terraforming_delta())
                owned_star.set_cost_science(self.tech.get_terraforming_delta())
            
                if owned_star not in owned_stars:
                    owned_stars.append(owned_star)
                else:
                    raise Exception(f"Duplicate star found in Star Data for star named {owned_star.name}")

        if owned_stars == {}:
            raise Exception(f"No stars found owned by player named {self.name}")
        return owned_stars

    def reset_player(self):
            self.raw_player_dict: dict = self.__get_player_data(self.raw_game_data)
            self.uid: int = self.raw_player_dict["uid"]
            self.tech: Tech = Tech(self.raw_player_dict["tech"])
            self.owned_stars: dict[str, Star] = self.__get_player_owned_stars_data(self.raw_game_data)
            self.total_economy: int = self.raw_player_dict["total_economy"]
            self.total_industry: int = self.raw_player_dict["total_industry"]
            self.total_science: int = self.raw_player_dict["total_science"]
            self.total_strength: int = self.raw_player_dict["total_strength"]
            self.current_cash: int = self.raw_player_dict["cash"]

    def get_income(self) -> int:
        return self.total_economy*10 + self.tech.get_banking_income()
    
    def get_ship_production(self) -> int:
        return self.tech.get_industry_rate()*self.total_industry

    def get_cheapest_economy(self) -> Star:
        return min(self.owned_stars, key=lambda x: x.economy_cost)

    def buy_cheapest_economy(self, spend_amount: int) -> int:
        amount_left = spend_amount
        cheapest_star = self.get_cheapest_economy()

        while amount_left > 0 and amount_left >= cheapest_star.economy_cost:
            if amount_left >= cheapest_star.economy_cost:
                amount_left -= cheapest_star.economy_cost
                self.current_cash -= cheapest_star.economy_cost 
                cheapest_star.buy_economy(self.tech.get_terraforming_delta())
                self.total_economy += 1
                cheapest_star = self.get_cheapest_economy()
    
    def get_cheapest_industry(self) -> Star:
        return min(self.owned_stars, key=lambda x: x.industry_cost)
    
    def buy_cheapest_industry(self, spend_amount: int) -> int:
        amount_left = spend_amount
        cheapest_star = self.get_cheapest_industry()

        while amount_left > 0 and amount_left >= cheapest_star.industry_cost:
            if amount_left >= cheapest_star.industry_cost:
                amount_left -= cheapest_star.industry_cost
                self.current_cash -= cheapest_star.industry_cost
                cheapest_star.buy_industry(self.tech.get_terraforming_delta())
                self.total_industry += 1
                cheapest_star = self.get_cheapest_industry()

    def get_effective_strength(self, enemy_weapons_tech: int) -> float:
        x = self.tech.Weapons.level
        y = enemy_weapons_tech

        effective_ship_strength = (x*y + x + y + 1)/(2*y*y + 2*y)
        return effective_ship_strength*self.total_strength
    
    def fitness_function(self) -> None:
        total_ships = 0
        first_step = True
        for i in range(self.dna.strands):
            if not first_step:
                self.current_cash = self.get_income()
            else:
                first_step = False
            rand_economy = self.dna.get_gene(i, 0)

            economy_distribution = int(rand_economy*self.current_cash)
            industry_distribution = max(0, self.current_cash  - economy_distribution)

            self.buy_cheapest_economy(economy_distribution)
            self.buy_cheapest_industry(industry_distribution)

            total_ships += self.get_ship_production()
        self.fitness = total_ships
        self.reset_player()





