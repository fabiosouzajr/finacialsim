from decimal import Decimal

from app.core.validators import (
    DEFAULT_RULES,
    SimulationInput,
    ValidationLevel,
    validate_simulation,
)


RULES = DEFAULT_RULES


def test_valid_input_returns_no_errors() -> None:
    inp = SimulationInput(
        valor_veiculo=Decimal("50000"),
        valor_entrada=Decimal("10000"),
        prazo_meses=48,
        taxa_mensal=Decimal("0.018"),
        dias_carencia=30,
    )
    issues = validate_simulation(inp, RULES)
    errors = [i for i in issues if i.level is ValidationLevel.ERROR]
    assert errors == []


def test_entrada_below_minimum_blocks() -> None:
    inp = SimulationInput(
        valor_veiculo=Decimal("50000"),
        valor_entrada=Decimal("3000"),
        prazo_meses=48,
        taxa_mensal=Decimal("0.018"),
        dias_carencia=30,
    )
    issues = validate_simulation(inp, RULES)
    assert any(i.field == "valor_entrada" and i.level is ValidationLevel.ERROR for i in issues)


def test_prazo_out_of_range_blocks() -> None:
    inp = SimulationInput(
        valor_veiculo=Decimal("50000"),
        valor_entrada=Decimal("10000"),
        prazo_meses=84,
        taxa_mensal=Decimal("0.018"),
        dias_carencia=30,
    )
    issues = validate_simulation(inp, RULES)
    assert any(i.field == "prazo_meses" and i.level is ValidationLevel.ERROR for i in issues)


def test_taxa_too_high_blocks() -> None:
    inp = SimulationInput(
        valor_veiculo=Decimal("50000"),
        valor_entrada=Decimal("10000"),
        prazo_meses=48,
        taxa_mensal=Decimal("0.10"),
        dias_carencia=30,
    )
    issues = validate_simulation(inp, RULES)
    assert any(i.field == "taxa_mensal" and i.level is ValidationLevel.ERROR for i in issues)


def test_valor_financiado_below_minimum_blocks() -> None:
    inp = SimulationInput(
        valor_veiculo=Decimal("8000"),
        valor_entrada=Decimal("4000"),
        prazo_meses=24,
        taxa_mensal=Decimal("0.018"),
        dias_carencia=30,
    )
    issues = validate_simulation(inp, RULES)
    assert any(i.field == "valor_financiado" and i.level is ValidationLevel.ERROR for i in issues)


def test_taxa_below_minimum_is_warning_not_error() -> None:
    # taxa_minima_mes is WARNING (not ERROR) per grilling amendment
    inp = SimulationInput(
        valor_veiculo=Decimal("50000"),
        valor_entrada=Decimal("10000"),
        prazo_meses=48,
        taxa_mensal=Decimal("0.003"),  # below 0.005
        dias_carencia=30,
    )
    issues = validate_simulation(inp, RULES)
    taxa_issues = [i for i in issues if i.field == "taxa_mensal"]
    assert any(i.level is ValidationLevel.WARNING for i in taxa_issues)
    assert not any(i.level is ValidationLevel.ERROR for i in taxa_issues)
