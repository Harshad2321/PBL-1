"""
Test Script for API Server
Run this to verify the backend is working before GameMaker integration
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"
SESSION_ID = "test_session_123"


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_health_check():
    """Test if server is running."""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()
        print(f"✓ Server is running!")
        print(f"  Status: {data['status']}")
        print(f"  Active sessions: {data['active_sessions']}")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running!")
        print("  Start it with: python nurture/api_server.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_new_game():
    """Test creating a new game."""
    print_section("2. Creating New Game")
    try:
        response = requests.post(
            f"{BASE_URL}/game/new",
            json={
                "session_id": SESSION_ID,
                "role": "FATHER"
            },
            timeout=10
        )
        data = response.json()

        if data.get('success'):
            print(f"✓ Game created successfully!")
            print(f"  Session ID: {data['session_id']}")
            print(f"  Message: {data['message']}")
            return True
        else:
            print(f"✗ Failed to create game: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_scenario():
    """Test getting current scenario."""
    print_section("3. Getting Current Scenario")
    try:
        response = requests.get(
            f"{BASE_URL}/game/scenario",
            params={"session_id": SESSION_ID},
            timeout=10
        )
        data = response.json()

        if data.get('success'):
            scenario = data['scenario']
            print(f"✓ Scenario loaded successfully!")
            print(f"\n  {scenario['act']} - Day {scenario['day']}/{scenario['total_days_in_act']}")
            print(f"  Title: {scenario['title']}")
            print(f"  Description: {scenario['description'][:100]}...")
            print(f"\n  Scenario: {scenario['scenario_text'][:150]}...")
            print(f"\n  Choices:")
            for i, choice in enumerate(scenario['choices'], 1):
                print(f"    {i}. {choice['text']}")
            return True
        else:
            print(f"✗ Failed to get scenario: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_make_choice():
    """Test making a choice."""
    print_section("4. Making a Choice")
    try:
        choice_number = 2
        print(f"  Selecting choice #{choice_number}...")

        response = requests.post(
            f"{BASE_URL}/game/choice",
            json={
                "session_id": SESSION_ID,
                "choice_number": choice_number
            },
            timeout=10
        )
        data = response.json()

        if data.get('success'):
            print(f"✓ Choice processed!")
            print(f"  {data.get('message')}")
            return True
        else:
            print(f"✗ Failed to process choice: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_send_message():
    """Test sending a message to AI partner."""
    print_section("5. Sending Message to AI Partner")
    try:
        message = "I think we should work together on raising our child."
        print(f"  Your message: \"{message}\"")

        response = requests.post(
            f"{BASE_URL}/game/message",
            json={
                "session_id": SESSION_ID,
                "message": message
            },
            timeout=15
        )
        data = response.json()

        if data.get('success'):
            print(f"\n✓ AI Partner responded!")
            print(f"  Response: \"{data['response']}\"")
            return True
        else:
            print(f"✗ Failed to get response: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_status():
    """Test getting game status."""
    print_section("6. Getting Game Status")
    try:
        response = requests.get(
            f"{BASE_URL}/game/status",
            params={"session_id": SESSION_ID},
            timeout=10
        )
        data = response.json()

        if data.get('success'):
            print(f"✓ Status retrieved!")

            story = data.get('story_status', {})
            print(f"\n  Story Progress:")
            for key, value in story.items():
                print(f"    {key}: {value}")

            relationship = data.get('relationship_status', {})
            print(f"\n  Relationship Metrics:")
            for key, value in relationship.items():
                if isinstance(value, float):
                    print(f"    {key}: {value:.1f}")
                else:
                    print(f"    {key}: {value}")

            learning = data.get('learning_status', {})
            print(f"\n  Learning Status:")
            for key, value in learning.items():
                print(f"    {key}: {value}")

            return True
        else:
            print(f"✗ Failed to get status: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Run all API tests."""
    print("\n" + "="*60)
    print("  NURTURE API SERVER TEST SUITE")
    print("="*60)

    results = []

    # 1. Health check
    results.append(("Health Check", test_health_check()))
    if not results[-1][1]:
        print("\n⚠ Server not running. Cannot continue tests.")
        return

    time.sleep(0.5)

    # 2. Create game
    results.append(("New Game", test_new_game()))
    if not results[-1][1]:
        print("\n⚠ Cannot continue without a game session.")
        return

    time.sleep(0.5)

    # 3. Get scenario
    results.append(("Get Scenario", test_get_scenario()))

    time.sleep(0.5)

    # 4. Make choice
    results.append(("Make Choice", test_make_choice()))

    time.sleep(0.5)

    # 5. Send message
    results.append(("Send Message", test_send_message()))

    time.sleep(0.5)

    # 6. Get status
    results.append(("Get Status", test_get_status()))

    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {test_name}")

    print(f"\n  Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n  🎉 All tests passed! Backend is ready for GameMaker integration.")
    else:
        print("\n  ⚠ Some tests failed. Check the errors above.")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
