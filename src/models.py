from dataclasses import dataclass, field


@dataclass
class ChargeData:
    case_no: str
    offense_date: str
    code: str
    description: str
    grade: str
    degree: str


@dataclass
class PersonData:
    name: str
    sex: str
    dob: str
    height: str
    weight: str
    hair_color: str
    hair_length: str
    eye_color: str
    complexion: str
    booking_no: str
    perm_id: str
    police_county_id: str
    race: str
    ethnicity: str
    marital_status: str
    citizen: str
    country_of_birth: str
    curr_loc: str
    county: str
    commit_date: str
    proj_release_date: str
    bond_type: str
    bond_status: str
    posted_by: str
    post_date: str
    bond_total: str
    charges: list[ChargeData] = field(default_factory=list)
