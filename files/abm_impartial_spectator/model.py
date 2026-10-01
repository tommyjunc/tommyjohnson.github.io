"""Mesa model for student evaluations and professor adaptation."""

from mesa import Model
from mesa.datacollection import DataCollector

if __package__:
    from .agents import ProfessorAgent, StudentAgent
else:
    from agents import ProfessorAgent, StudentAgent


class ImpartialSpectatorModel(Model):
    """Simulate how ratings become a shared signal that shapes behavior.

    Each student rates every professor once per step. The platform updates each
    aggregate as an exponential moving average of the new ratings. Professors
    internalize that signal and adapt behavior toward it.
    """

    def __init__(
        self,
        n_students=100,
        n_professors=5,
        conformity=0.25,
        adaptation_rate=0.1,
        noise=0.35,
        seed=None,
    ):
        if n_students < 1 or n_professors < 1:
            raise ValueError("n_students and n_professors must be at least 1")
        if not 0 <= conformity <= 1:
            raise ValueError("conformity must be between 0 and 1")
        if not 0 <= adaptation_rate <= 1:
            raise ValueError("adaptation_rate must be between 0 and 1")
        if noise < 0:
            raise ValueError("noise must be non-negative")

        super().__init__(seed=seed)
        self.conformity = conformity
        self.adaptation_rate = adaptation_rate
        self.noise = noise
        self.students = [
            StudentAgent(self, bias=self.random.gauss(0, 0.5))
            for _ in range(n_students)
        ]
        self.professors = [
            ProfessorAgent(
                self,
                professor_id=index,
                latent_quality=self.random.uniform(2.0, 5.0),
            )
            for index in range(n_professors)
        ]

        reporters = {}
        for professor in self.professors:
            identifier = professor.professor_id
            reporters[f"professor_{identifier}_aggregate_rating"] = (
                lambda model, p=professor: p.aggregate_rating
            )
            reporters[f"professor_{identifier}_behavior"] = (
                lambda model, p=professor: p.behavior
            )
            reporters[f"professor_{identifier}_latent_quality"] = (
                lambda model, p=professor: p.latent_quality
            )
            reporters[f"professor_{identifier}_internalized_spectator"] = (
                lambda model, p=professor: p.internalized_spectator
            )
        self.datacollector = DataCollector(model_reporters=reporters)
        self.datacollector.collect(self)

    def step(self):
        """Collect one round of student ratings and update professor behavior."""
        ratings = {professor: [] for professor in self.professors}
        for student in self.students:
            for professor in self.professors:
                ratings[professor].append(
                    student.evaluate(professor, self.noise, self.conformity)
                )

        for professor, professor_ratings in ratings.items():
            mean_rating = sum(professor_ratings) / len(professor_ratings)
            professor.aggregate_rating += 0.25 * (
                mean_rating - professor.aggregate_rating
            )
            professor.adapt(self.adaptation_rate)

        self.datacollector.collect(self)
