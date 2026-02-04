# Infection Connection Weight Calculator

def normalize(value, max_value):
    """Normalize a value between 0 and 1"""
    return min(max(value / max_value, 0), 1)


def calculate_weight(F, D, P, E, R, S, method="multiplicative"):
    """
    Calculate connection weight using selected method
    """

    if method == "multiplicative":
        weight = F * D * P * E * R * S

    elif method == "linear":
        weight = (0.25 * F +
                  0.20 * D +
                  0.20 * P +
                  0.15 * E +
                  0.10 * R +
                  0.10 * S)

    else:
        raise ValueError("Invalid method selected")

    return round(weight, 4)


def get_input():
    print("\n--- Infection Connection Weight Calculator ---\n")

    print("Enter the following values:")

    freq = float(input("Contact Frequency (times per day, max 10): "))
    dur = float(input("Contact Duration (minutes, max 120): "))
    prox = float(input("Proximity score (0 to 1): "))
    env = float(input("Environment score (0 to 1): "))
    prot = float(input("Protection score (0 to 1): "))
    susc = float(input("Susceptibility score (0 to 1): "))

    # Normalize frequency and duration
    F = normalize(freq, 10)
    D = normalize(dur, 120)

    P = normalize(prox, 1)
    E = normalize(env, 1)
    R = normalize(prot, 1)
    S = normalize(susc, 1)

    print("\nChoose calculation method:")
    print("1 - Multiplicative (Recommended)")
    print("2 - Linear Weighted")

    choice = input("Enter choice (1 or 2): ")

    method = "multiplicative" if choice == "1" else "linear"

    weight = calculate_weight(F, D, P, E, R, S, method)

    print("\n----- RESULT -----")
    print(f"Computed Connection Weight: {weight}")
    print("------------------\n")


if __name__ == "__main__":
    get_input()
