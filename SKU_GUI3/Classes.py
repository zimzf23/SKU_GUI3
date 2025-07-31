from dataclasses import dataclass, field
from typing import Dict, Optional

# --- nested pieces ---
@dataclass
class BasicData:
    ref: str
    name: str = ''
    description: str = ''
    cls: int = 0  # avoid keyword 'class'
    type: int = 0

@dataclass
class DecodedData:
    level: int = 0
    type: str = 'X'
    cat: int = 0
    subcat: int = 0

@dataclass
class AvailableContent:
    external: int = 0
    mechanical: int = 0
    electrical: int = 0
    shipping: int = 0
    supplier: int = 0
    finance: int = 0
    certs: int = 0
    enviromental: int = 0  # intentional spelling if matches source

@dataclass
class ExternalManufacturerData:
    manufacturer: str = ''
    name: str = ''
    number: str = ''
    description: str = ''
    ean: int = 0

@dataclass
class MechanicalData:
    weight: float = 0.0
    dimensions: str = ''
    material: str = ''
    color: str = ''
    finish: str = ''
    shape: str = ''
    size: str = ''

@dataclass
class ElectricalData:
    voltage: float = 0.0
    current: float = 0.0
    power: float = 0.0
    frequency: float = 0.0
    phase: float = 0.0
    protection: str = ''
    efficiency: str = ''

@dataclass
class ShippingData:
    shipping_weight: float = 0.0
    shipping_dimensions: str = ''
    shipping_method: str = ''
    shipping_cost: float = 0.0

@dataclass
class SupplierData:
    supplier: str = ''
    contact: str = ''
    phone: str = ''
    email: str = ''
    address: str = ''

@dataclass
class FinanceData:
    cost: float = 0.0
    price: float = 0.0
    margin: float = 0.0
    currency: str = ''
    payment_terms: str = ''

@dataclass
class CertsData:
    certifications: str = ''
    compliance: str = ''
    standards: str = ''

@dataclass
class EnviromentalData:
    recyclable: bool = False
    hazardous: bool = False
    disposal_instructions: str = ''

# --- aggregate per-ref item ---
@dataclass
class FullItem:
    basic: BasicData
    decoded: DecodedData = field(default_factory=DecodedData)
    available: AvailableContent = field(default_factory=AvailableContent)
    external_manufacturer: ExternalManufacturerData = field(default_factory=ExternalManufacturerData)
    mechanical: MechanicalData = field(default_factory=MechanicalData)
    electrical: ElectricalData = field(default_factory=ElectricalData)
    shipping: ShippingData = field(default_factory=ShippingData)
    supplier: SupplierData = field(default_factory=SupplierData)
    finance: FinanceData = field(default_factory=FinanceData)
    certs: CertsData = field(default_factory=CertsData)
    enviromental: EnviromentalData = field(default_factory=EnviromentalData)

    @property
    def status(self) -> str:
        return "Complete" if any([
            self.basic.name,
            self.external_manufacturer.name,
            self.finance.price > 0
        ]) else "Incomplete"

# --- container for multiple refs ---
class Catalog:
    def __init__(self):
        self.items: Dict[str, FullItem] = {}

    def get_or_create(self, ref: str, **basic_kwargs) -> FullItem:
        if ref not in self.items:
            self.items[ref] = FullItem(basic=BasicData(ref=ref, **basic_kwargs))
        return self.items[ref]

    def __getitem__(self, ref: str) -> FullItem:
        return self.items[ref]

    def __contains__(self, ref: str) -> bool:
        return ref in self.items
