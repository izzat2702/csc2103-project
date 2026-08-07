from activity_algorithms import manual_sort_by_end, select_activities


def format_selection_table(selected):
    if not selected:
        return "No activities selected."

    lines = [f"{'Name':<10}{'Start':<10}{'End':<10}"]
    for name, start, end in selected:
        lines.append(f"{name:<10}{start:<10}{end:<10}")
    lines.append(f"\nTotal selected: {len(selected)}")
    return "\n".join(lines)


def read_activities_from_console():
    activities = []

    while True:
        try:
            count = int(input("How many activities? "))
            if count < 0:
                print("Please enter a non-negative number.")
                continue
            break
        except ValueError:
            print("Please enter a whole number.")

    for i in range(count):
        while True:
            try:
                raw = input(
                    f"Activity {i + 1} - enter name, start time, end time "
                    "(space separated, e.g. 'A1 1 4'): "
                )
                name, start_str, end_str = raw.split()
                start, end = int(start_str), int(end_str)
                if start >= end:
                    print("Start time must be before end time.")
                    continue
                activities.append((name, start, end))
                break
            except ValueError:
                print("Invalid format. Expected: name start end")

    return activities


def main():
    print("Activity Selection Problem (Greedy)")
    print("------------------------------------")
    activities = read_activities_from_console()
    selected = select_activities(activities)
    print()
    print(format_selection_table(selected))


if __name__ == "__main__":
    main()
