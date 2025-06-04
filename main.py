from cli.interface import IncidentCLI
from incident.models import clear_console, validate_input, validate_integer_input


def display_main_menu() -> None:
    print("""\n=== Incident Management System ===)
    "1. Create new incident")
    "2. List open incidents")
    "3. Assign incident to operator")
    "4. Resolve incident")
    "5. Filter incidents")
    "6. Display history")
    "7. Exit""")


def handle_create_incident(cli: IncidentCLI) -> None:
    print("\n=== Create New Incident ===")
    incident_type = validate_input(
        "Incident type (infrastructure/application/security): ",
        ["infrastructure", "application", "security"]
    )
    priority_level = validate_input(
        "Priority level (low/medium/high): ",
        ["low", "medium", "high"]
    )
    description = input("Description: ").strip()
    if description:
        cli.register_new_incident(incident_type, priority_level, description)
    else:
        print("✖ Description cannot be empty.")


def handle_assign_incident(cli: IncidentCLI) -> None:

    print("\n=== Assign Incident to Operator ===")
    print("=== Pending Incidents to Assign ===")
    cli.show_assignable_incidents()
    
    print("""\n=== Operator Capabilities ===
    - alice: infrastructure specialist
    - bob: application specialist
    - carol: security specialist""")
    
    incident_id = input("\nIncident ID: ").strip()
    if incident_id:
        operator_name = validate_input(
            "Operator name (alice/bob/carol): ",
            ["alice", "bob", "carol"]
        )
        cli.assign_incident_to_operator_by_id(incident_id, operator_name)
    else:
        print("✖ Incident ID cannot be empty.")


def handle_resolve_incident(cli: IncidentCLI) -> None:

    print("\n=== Resolve Incident ===")
    cli.show_resolvable_incidents()
    incident_id = input("Incident ID to resolve: ").strip()
    if incident_id:
        cli.resolve_incident_by_id(incident_id)
    else:
        print("✖ Incident ID cannot be empty.")


def handle_filter_incidents(cli: IncidentCLI) -> None:

    print("""\n=== Filter Incidents ===
    1. Filter by status
    2. Filter by operator
    3. Filter by date range
    4. Filter by description text""")
    
    filter_choice = validate_input(
        "Choose filter option (1-4): ",
        ["1", "2", "3", "4"]
    )
    
    if filter_choice == "1":
        status = validate_input(
            "Status (pending/in_progress/escalated/resolved): ",
            ["pending", "in_progress", "escalated", "resolved"]
        )
        cli.filter_and_display_incidents_by_status(status)
    elif filter_choice == "2":
        operator = validate_input(
            "Operator name (alice/bob/carol): ",
            ["alice", "bob", "carol"]
        )
        cli.filter_and_display_incidents_by_operator(operator)
    elif filter_choice == "3":
        cli.filter_and_display_incidents_by_date_range()
    elif filter_choice == "4":
        search_text = input("Search pattern (regex): ").strip()
        if search_text:
            cli.filter_and_display_incidents_by_text(search_text)
        else:
            print("✖ Search pattern cannot be empty.")


def main() -> None:

    cli = IncidentCLI()
    
    print("Welcome to the Incident Management System!")
    print("Loading existing incidents...")
    
    while True:
        try:
            cli.run_escalation_process()
            
            display_main_menu()
            choice = validate_integer_input("Select an option (1-7): ")
            
            if choice == 1:
                handle_create_incident(cli)
            elif choice == 2:
                print("\n=== Open Incidents ===")
                cli.show_pending_incidents_by_priority()
            elif choice == 3:
                handle_assign_incident(cli)
            elif choice == 4:
                handle_resolve_incident(cli)
            elif choice == 5:
                handle_filter_incidents(cli)
            elif choice == 6:
                print("\n=== Incident History ===")
                cli.display_history()
            elif choice == 7:
                print("\n=== Saving and Exiting ===")
                cli.save_all_incidents()
                print("✔ All incidents saved successfully.")
                print("System terminated")
                break
            else:
                print("Invalid option. Please choose 1-7.")
                
            input("\nPress Enter to continue...")
            clear_console()
            
        except KeyboardInterrupt:
            print("\n\n=== Emergency Exit ===")
            cli.save_all_incidents()
            print("✔ All incidents saved successfully.")
            print("System terminated")
            break
        except Exception as error:
            print(f"An unexpected error occurred: {error}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()