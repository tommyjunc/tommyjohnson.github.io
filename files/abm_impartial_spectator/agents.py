"""Student and professor agents for the reputation model."""

from mesa import Agent


class StudentAgent(Agent):
    """A student whose ratings reflect experience, preferences, and noise."""

    def __init__(self, model, bias):
        super().__init__(model)
        self.bias = bias

    def evaluate(self, professor, noise, conformity):
        """Return a 1–5 rating, optionally pulled toward the public consensus."""
        experience = (
            0.5 * professor.latent_quality
            + 0.5 * professor.behavior
            + self.bias
            + self.model.random.gauss(0, noise)
        )
        evaluation = (1 - conformity) * experience + conformity * professor.aggregate_rating
        return min(5.0, max(1.0, evaluation))


class ProfessorAgent(Agent):
    """A professor who adapts behavior toward an internalized public signal."""

    def __init__(self, model, professor_id, latent_quality):
        super().__init__(model)
        self.professor_id = professor_id
        self.latent_quality = latent_quality
        self.behavior = latent_quality
        self.aggregate_rating = 3.0
        self.internalized_spectator = 3.0

    def adapt(self, adaptation_rate):
        """Update the internal spectator and move behavior toward its signal."""
        self.internalized_spectator += 0.25 * (
            self.aggregate_rating - self.internalized_spectator
        )
        self.behavior += adaptation_rate * (
            self.internalized_spectator - self.behavior
        )
        self.behavior = min(5.0, max(1.0, self.behavior))
