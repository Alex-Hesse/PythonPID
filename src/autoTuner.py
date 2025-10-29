from PythonPID.src.pid_controller import PID_Controller
import time
import math


class AdaptivePID(PID_Controller):
    """
    PID controller that can automatically tune itself based on live response.
    """

    def __init__(self, *args, tune_rate=0.01, error_threshold=0.05, **kwargs):
        super().__init__(*args, **kwargs)
        self._tune_rate = tune_rate
        self._error_threshold = error_threshold
        self._prev_error_sign = None
        self._oscillation_counter = 0

    def compute(self, current_value: float, target_value: float) -> float:
        # Run the normal PID computation
        output = super().compute(current_value, target_value)

        # Run live tuning logic
        self._auto_tune(current_value, target_value)

        return output

    def _auto_tune(self, current_value: float, target_value: float) -> None:
        """
        Adjust gains based on live error trends.
        """
        error = target_value - current_value

        # Detect oscillations by error sign changes
        sign = math.copysign(1, error)
        if self._prev_error_sign is not None and sign != self._prev_error_sign:
            self._oscillation_counter += 1
        self._prev_error_sign = sign

        # Simple heuristic adjustments
        if abs(error) > self._error_threshold:
            # System is too sluggish → increase Kp
            self._kp += self._tune_rate * abs(error)
        elif self._oscillation_counter > 3:
            # Too many oscillations → back off Kp or increase D
            self._kp *= 0.95
            self._kd += self._tune_rate * 0.1
            self._oscillation_counter = 0

        # Optional: adjust Ki based on steady-state error
        if abs(error) < self._error_threshold:
            self._ki += self._tune_rate * 0.001



# MAIN TEST SIMULATION-
if __name__ == "__main__":
    import random
    print("Starting Adaptive PID simulation...\n")
    pid = AdaptivePID(kp=0.5, ki=0.05, kd=0.02, min_output=-100, max_output=100, tau=0.05)

    target = 10.0
    process_value = 0.0
    dt = 0.05

    print(f"{'Step':>4} | {'Value':>7} | {'Cmd':>7} | {'Kp':>6} | {'Ki':>6} | {'Kd':>6}")
    print("-" * 45)

    for step in range(200):
        cmd = pid.compute(process_value, target)

        # Simple process model: inertia + noise
        process_value += 0.1 * cmd * dt
        process_value += random.uniform(-0.02, 0.02)

        if step % 10 == 0:
            print(
                f"{step:4d} | {process_value:7.3f} | {cmd:7.3f} | "
                f"{pid._kp:6.3f} | {pid._ki:6.3f} | {pid._kd:6.3f}"
            )

        time.sleep(dt)

    print("\nSimulation complete.")