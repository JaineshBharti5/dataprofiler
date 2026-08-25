class HealthScore:
    """
    Calculate an overall data-health score from 0 to 100.

    Components:
        completeness
        uniqueness
        validation
        anomalies
    """

    def __init__(
        self,
        completeness_weight=0.30,
        uniqueness_weight=0.20,
        validation_weight=0.30,
        anomaly_weight=0.20
    ):
        weights = [
            completeness_weight,
            uniqueness_weight,
            validation_weight,
            anomaly_weight
        ]

        if any(weight < 0 for weight in weights):
            raise ValueError(
                "Weights cannot be negative."
            )

        if round(sum(weights), 10) != 1.0:
            raise ValueError(
                "Health score weights must sum to 1.0."
            )

        self.completeness_weight = completeness_weight
        self.uniqueness_weight = uniqueness_weight
        self.validation_weight = validation_weight
        self.anomaly_weight = anomaly_weight

    @staticmethod
    def _clamp(value):
        return max(0.0, min(100.0, float(value)))

    def calculate(
        self,
        completeness,
        uniqueness,
        validation=100.0,
        anomalies=0.0
    ):
        """
        Calculate health score.

        Parameters:
            completeness:
                Completeness percentage, 0-100.

            uniqueness:
                Uniqueness percentage, 0-100.

            validation:
                Validation pass percentage, 0-100.

            anomalies:
                Anomaly percentage, 0-100.

        Returns:
            Overall health score from 0 to 100.
        """

        completeness = self._clamp(
            completeness
        )

        uniqueness = self._clamp(
            uniqueness
        )

        validation = self._clamp(
            validation
        )

        anomalies = self._clamp(
            anomalies
        )

        anomaly_score = 100.0 - anomalies

        score = (
            completeness
            * self.completeness_weight
            +
            uniqueness
            * self.uniqueness_weight
            +
            validation
            * self.validation_weight
            +
            anomaly_score
            * self.anomaly_weight
        )

        return round(
            self._clamp(score),
            2
        )

    def report(
        self,
        completeness,
        uniqueness,
        validation=100.0,
        anomalies=0.0
    ):
        """
        Return a complete health-score report.
        """

        completeness = self._clamp(
            completeness
        )

        uniqueness = self._clamp(
            uniqueness
        )

        validation = self._clamp(
            validation
        )

        anomalies = self._clamp(
            anomalies
        )

        score = self.calculate(
            completeness,
            uniqueness,
            validation,
            anomalies
        )

        if score >= 90:
            status = "EXCELLENT"
        elif score >= 75:
            status = "GOOD"
        elif score >= 50:
            status = "FAIR"
        else:
            status = "POOR"

        return {
            "score": score,
            "status": status,
            "components": {
                "completeness": round(
                    completeness,
                    2
                ),
                "uniqueness": round(
                    uniqueness,
                    2
                ),
                "validation": round(
                    validation,
                    2
                ),
                "anomaly_rate": round(
                    anomalies,
                    2
                )
            }
        }