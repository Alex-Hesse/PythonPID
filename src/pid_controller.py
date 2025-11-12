import time
import math
"""
PID modeled after Matlab PID introduction
https://youtu.be/wkfEZmsQqiA?si=G9xtIAdn5ta9msH8
"""


class PID_Controller:
    """
    A simple PID (Proportional-Integral-Derivative) controller.

    Attributes:
        kp (float): Proportional gain
        ki (float): Integral gain
        kd (float): Derivative gain
        min_output (float): Minimum output limit
        max_output (float): Maximum output limit
        tau (float): Derivative filter time constant (seconds)
    """

    def __init__(self, kp: float, ki: float, kd: float, min_output: float, max_output: float, tau: float = 0.02, integrator_reset_delta: float = 1.0) -> None:
        # PID coefficients
        self._kp = kp
        self._ki = ki
        self._kd = kd

        # Output limits
        self._min_output = min_output
        self._max_output = max_output
        
        # Derivative filter parameter
        self._tau = tau  # Higher tau = more smoothing, less noise, slower response
        
        self._integrator_reset_delta = integrator_reset_delta
        # back calculation windup
        self._k_aw = 0.90
        
        self._max_derivative = max_output * 0.2
        self._min_derivative = min_output * 0.2
        self._max_out_rate = (max_output - min_output) * 1.0

        # Internal state
        self._last_error = 0.0
        self._last_time = time.time()
        self._integral = 0.0
        self._last_derivative = 0.0
        self._last_value = 0.0
        self._last_target = 0.0
        self._last_output = 0.0
        self._clamped = False

    def compute(self, current_value: float, target_value: float) -> float:
        """
        Compute the control command based on the current and target values.

        Args:
            current_value (float): The current process variable.
            target_value (float): The desired set point.

        Returns:
            float: The control command output.
        """
        # Calculate time step
        current_time = time.time()
        dt = current_time - self._last_time
        if dt <= 0.0:
            dt = 1e-6  # Avoid divide-by-zero errors

        # Calculate error term
        error = target_value - current_value
        

        # --- Proportional term ---
        p_term = self._kp * error

        # --- Integral term ---
        
        # reset integral if target has changed more then resetDelta
        if abs(self._last_target - target_value) > self._integrator_reset_delta:
            self._integral *= 0.5  # or = 0 for hard reset?
        
        # back calculation if min/max_output already reached to not integrate further
        if not self._clamped:
            self._integral += error * dt
        i_term = self._ki * self._integral

        # --- Derivative term (with low-pass filter) ---
        
        # derivative on measurement
        derivative = -(current_value - self._last_value) / dt
        # derivative = (error - self._last_error) / dt  # spikes on target_value change

        # Filter derivative
        filtered_derivative = self._filter_derivative(derivative, dt)
        
        # clamp derivative protect noise / glitches
        clamped_derivative = max(self._min_derivative, min(filtered_derivative, self._max_derivative))

        d_term = self._kd * clamped_derivative

        # Total PID output
        output = p_term + i_term + d_term

        # Clamp the output within limits
        clamped_output = self._apply_clamping(output, error)
        if self._clamped:
            self._integral -= (output -clamped_output) * self._k_aw *dt
            
        # slew rate limiting
        delta_output = clamped_output - self._last_output
        if abs(delta_output) / dt > self._max_out_rate:
            clamped_output = self._last_output + math.copysign(self._max_out_rate * dt, delta_output)    

        # Update internal state
        self._last_error = error
        self._last_time = current_time
        self._last_derivative = derivative
        self._last_value = current_value
        self._last_target = target_value
        self._last_output = clamped_output

        return clamped_output

    def _apply_clamping(self, output: float, error: float) -> float:
        """
        Clamp the PID output to the configured limits.
        This will ensure that our integrator doesn't windup

        Args:
            output (float): The raw PID output.
            error (float): The current error (for anti-windup logic).

        Returns:
            float: The clamped PID output.
        """
        clamped_output = max(self._min_output, min(self._max_output, output))

        # Check if we hit the limit (for anti-windup)
        self._clamped = math.copysign(1, clamped_output) == math.copysign(1, error) and (
            clamped_output == self._min_output or clamped_output == self._max_output
        )

        return clamped_output

    def _filter_derivative(self, raw_derivative: float, dt: float) -> float:
        """
        Apply a first-order low-pass filter to the derivative term.

        Args:
            raw_derivative (float): The unfiltered derivative value.
            dt (float): Time step since last update.

        Returns:
            float: Filtered derivative value.
        """
        # Compute the smoothing factor (alpha)
        alpha = self._tau / (self._tau + dt)

        # Apply exponential smoothing
        filtered_derivative = (alpha * self._last_derivative + (1 - alpha) * raw_derivative)
        
        return filtered_derivative
    

# Test simulation
if __name__ == "__main__":
    import random
    # Example PID tuning (adjust as needed)
    pid = PID_Controller(kp=1.2, ki=0.3, kd=0.05, min_output=-100, max_output=100, tau=0.05)

    target = 10.0   # Desired set point
    process_value = 0.0  # Initial system value
    dt = 0.05       # Simulation step size (seconds)

    print("Starting PID simulation...\n")
    print(f"{'Time':>6} | {'Target':>7} | {'Value':>7} | {'Command':>8}")

    for step in range(1600):
        # Compute control output
        command = pid.compute(process_value, target)

        # Simulate a simple process: the command changes the process_value
        # The process has some inertia (slow response) and random noise
        process_value += 0.1 * command * dt
        process_value += random.uniform(-0.02, 0.02)  # Add small noise

        # Print every few steps
        if step % 10 == 0:
            print(f"{step*dt:6.2f} | {target:7.2f} | {process_value:7.2f} | {command:8.2f}")

        time.sleep(dt)  # Simulate real-time delay

    print("\nSimulation complete.")