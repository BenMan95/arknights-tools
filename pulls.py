from fractions import Fraction
import time

num_pulls = 5000

culling_threshold = 1e-12
num_culled = 0
prob_culled = 0

class State:

    def __init__(self, pity=0, pulls=0):
        self.pity = pity
        self.pulls = pulls

    def __repr__(self):
        return f'State(pity={self.pity}, pulls={self.pulls})'

    def __hash__(self):
        return self.pity + 100 * self.pulls

    def __eq__(self, other):
        return other and \
               self.pity == other.pity and \
               self.pulls == other.pulls

    def next_pull(self):
        numerator = max(1, self.pity-48)
        odds = numerator / 50
        #odds = Fraction(numerator, 50)

        return {
            State(pity=0, pulls=self.pulls+1): odds,
            State(pity=self.pity+1, pulls=self.pulls): 1-odds,
        }

class Possibilities:

    def __init__(self, odds={State(): 1}):
        #assert sum(p for p in odds.values()) == 1
        self.odds = odds

    def next_pull(self):
        global num_culled, prob_culled

        results = {}

        for state, p1 in self.odds.items():
            for next_state, p2 in state.next_pull().items():
                prob = p1 * p2

                if prob <= culling_threshold:
                    num_culled += 1
                    prob_culled += prob
                    continue

                if next_state in results:
                    results[next_state] += prob
                else:
                    results[next_state] = prob

        return Possibilities(results)

    def reduced_odds(self):
        max_pulls = max(state.pulls for state in self.odds.keys())
        results = [0] * (max_pulls + 1)
        for state, p in self.odds.items():
            results[state.pulls] += p
        return results

start = time.perf_counter()

results = Possibilities()
i = 0
try:
    for i in range(num_pulls):
        if i % 50 == 0:
            print(f'{i} pulls: {len(results.odds)} states')
        results = results.next_pull()
except KeyboardInterrupt:
    num_pulls = i
    print(f'Recieved KeyboardInterrupt, exiting at {num_pulls} pulls')

end = time.perf_counter()

print(f'Finished in {end-start:.6f} seconds')
print()

print(f'Culled states: {num_culled}')
print(f'Culled probability: {prob_culled:.6f}')

total_prob = sum(results.odds.values())
print(f'Remaining states: {len(results.odds)}')
print(f'Remaining probability: {total_prob:.6f}')
print()

#print(results.reduced_odds())

#for n, p in enumerate(results.reduced_odds()):
#    if p >= 0.000001:
#        print(f'{n}: {float(p):.6f}')
#    print(f'{n}: {p:.6f}')

probabilities = results.reduced_odds()
p_target = Fraction(5,60) * Fraction(3,10)
#p_target = Fraction(35,100)
p_total = 0
enum_six_stars = 0
for n, p in enumerate(probabilities):

    p_case = 1 - (1-p_target)**n
    #p_case = (1-p_target) ** n
    p_total += p*p_case
    enum_six_stars += n * p

print(f'Target probability: {p_total:.6%}')
print(f'Expected # of 6 stars: {enum_six_stars}')
print(f'Rate: {enum_six_stars/num_pulls}')
