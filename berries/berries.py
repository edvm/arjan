"""Main module."""

import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Protocol

import httpx


@dataclass(frozen=True, slots=True)
class Firmness:
    """A Firmness object."""
    name: str
    url: str


@dataclass(frozen=True, slots=True)
class Flavor:
    """A Flavor object."""
    name: str
    url: str
    potency: int


@dataclass(frozen=True, slots=True)
class Berry:
    """A Berry object."""
    id: int
    name: str
    firmness: Firmness
    flavors: list[Flavor]


class BerriesRepository(Protocol):

    async def get(self, id: int | str) -> Berry:
        """Asynchronously retrieves a Berry object by its ID or Name."""
        ...

    async def get_all(self) -> list[Berry]:
        """Asynchronously retrieves all Berries."""
        ...

    async def get_all_generator(self) -> AsyncGenerator[Berry, None]:
        """Asynchronously retrieves all berries using a generator."""
        ...


class BerriesAPI(BerriesRepository):
    def __init__(self, url: str = "https://pokeapi.co/api/v2/berry"):
        self._url = url
        self._client = httpx.AsyncClient(base_url=self._url)

    @property
    def url(self) -> str:
        return self._url

    async def get(self, id: int | str) -> Berry:
        """
        Asynchronously retrieves a Berry object by its ID or Name.

        Args:
            id (int | str): The ID or Name of the berry to retrieve.

        Returns:
            Berry: The Berry object with the specified ID.

        Raises:
            HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        response = await self._client.get(f"{self.url}/{id}")
        data = response.raise_for_status().json()
        return Berry(
            id=data["id"],
            name=data["name"],
            firmness=Firmness(name=data["firmness"]["name"], url=data["firmness"]["url"]),
            flavors=[
                Flavor(name=flavor["flavor"]["name"], url=flavor["flavor"]["url"], potency=flavor["potency"])
                for flavor in data["flavors"]
            ],
        )

    async def get_all(self) -> list[Berry]:
        """
        Asynchronously retrieves all Berries.

        Returns:
            list[Berry]: A list of all Berries.
        """
        return [berry async for berry in self.get_all_generator()]

    async def get_all_generator(self) -> AsyncGenerator[Berry, None]:
        """
        Asynchronously retrieves all berries using a generator.

        Yields:
            Berry: An instance of the Berry class containing details of each berry.

        Raises:
            HTTPError: If the HTTP request to fetch the berry names fails.
        """
        response = await self._client.get(self.url)
        data = response.raise_for_status().json()
        names = [berry["name"] for berry in data["results"]]

        tasks = [self.get(name) for name in names]
        for task in asyncio.as_completed(tasks):
            berry = await task
            yield berry


class BerriesService:
    def __init__(self, repository: BerriesRepository):
        self._repository = repository

    async def get(self, id: int | str) -> Berry: 
        return await self._repository.get(id)

    async def get_all(self) -> list[Berry]:
        return await self._repository.get_all()

    async def get_all_generator(self) -> AsyncGenerator[Berry, None]:
        async for berry in self._repository.get_all_generator():
            yield berry


class BerriesApp:
    def __init__(self, service: BerriesService, repository: BerriesRepository):
        self._service = service
        self._repository = repository

    @property
    def service(self) -> BerriesService:
        return self._service

    @property
    def repository(self) -> BerriesRepository:
        return self._repository


async def get_app() -> BerriesApp:
    repository = BerriesAPI()
    service = BerriesService(repository)
    return BerriesApp(service, repository)
