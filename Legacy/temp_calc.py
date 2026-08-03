from broadspec.core.models import PaymentData, OtherSite
from broadspec.core.calculator import PaymentCalculator

config = {
    'calculation': {
        'token_to_usd_rate': 20.0,
        'trm_adjustment': 300,
        'fine_amount': 30000,
        'transfer_cost_tax': 0.19
    },
    'app': {
        'transfer_cost': 6.99
    }
}
calc = PaymentCalculator(config)

# Inputs
trm_official = 3675.81
btk_trm = 3536.81
percentage = 0.60  # 60%
# tokens? need to decide which is main tokens.
# Let's assume site 1 is main tokens = 3711, site 2 is other site tokens = 634
tokens_main = 3711
other_sites = [OtherSite("TKS", 634)]

data = PaymentData(
    model_id="test",
    model_name="test",
    trm_official_cop=trm_official,
    btk_trm_cop=btk_trm,
    tokens=tokens_main,
    percentage=percentage,
    previous_fortnight_usd=0,
    other_sites=other_sites,
    advances=[],
    extras=[],
    fines_count=0,
    custom_fine_cop=0,
    override_high_tokens_trm=False,
    disable_bonus=False
)

result = calc.calculate(data)
print("Total COP:", result.total_cop)
print("Total USD:", result.total_usd)
print("TRM BroadSpec COP:", result.trm_broadspec_cop)
print("Transfer cost COP:", result.transfer_cost_cop)
print("Valor BroadSpec COP:", result.valor_broadspec_cop)
print("Fines total:", result.fines_total)
print("Advances total:", result.advances_total)
print("Extras total:", result.extras_total)
print("Other sites total USD:", result.other_sites_total_usd)
print("USD from tokens:", result.usd_from_tokens)
print("Net USD:", result.net_usd)
print("Total USD precalc:", result.total_usd_precalc)
print("Total tokens all sites:", result.total_tokens_all_sites)
print("Bonus percentage:", result.bonus_percentage)
print("Final percentage:", result.final_percentage)
print("Original percentage:", result.original_percentage)