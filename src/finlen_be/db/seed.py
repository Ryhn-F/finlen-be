import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finlen_be.core.database import AsyncSessionLocal
from finlen_be.db.seed_data import SEED_SCENARIOS
from finlen_be.models.scenario import Scenario

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_scenarios(db: AsyncSession) -> int:
    """Seed predefined scenarios if they do not already exist."""
    seeded_count = 0
    for scenario_data in SEED_SCENARIOS:
        result = await db.execute(
            select(Scenario).where(Scenario.slug == scenario_data["slug"])
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            new_scenario = Scenario(**scenario_data)
            db.add(new_scenario)
            seeded_count += 1
            logger.info("Seeding new scenario: %s (%s)", scenario_data["title"], scenario_data["slug"])
        else:
            # Update fields in case definitions were enriched
            for key, value in scenario_data.items():
                setattr(existing, key, value)
            logger.debug("Scenario '%s' already exists, updated content.", scenario_data["slug"])

    await db.commit()
    logger.info("Seeding completed. Added %d new scenarios.", seeded_count)
    return seeded_count


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await seed_scenarios(session)


if __name__ == "__main__":
    asyncio.run(main())
