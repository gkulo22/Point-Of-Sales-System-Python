from dataclasses import dataclass, field


@dataclass
class GetCampaignErrorMessage(Exception):
    campaign_id: str
    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"Campaign with id: {self.campaign_id} does not exist."