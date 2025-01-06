import tkinter as tk
import random
import math
from itertools import permutations
from itertools import combinations, permutations

class TSPPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TSPP in L1 R2")

        # Canvas where the points and paths will be drawn
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack()

        # Crosshair tracking
        self.canvas.bind("<Motion>", self.update_crosshair)

        # Points and paths
        self.points = []
        self.paths = []
        self.total_distance = 0
        self.current_point = None
        self.end_point = None
        self.start_point = None

        # Labels and buttons (increased size by 20%)
        self.total_distance_label = tk.Label(root, text=f"Total Distance: {self.total_distance}", font=("Arial", 12))
        self.total_distance_label.pack()

        self.point_input_label = tk.Label(root, text="Number of Points:", font=("Arial", 12))
        self.point_input_label.pack()

        self.point_input = tk.Entry(root, font=("Arial", 12))
        self.point_input.pack()

        self.generate_button = tk.Button(root, text="Generate Points", font=("Arial", 12), command=self.generate_points)
        self.generate_button.pack()


        self.labels_visible = False  # Track whether labels are visible or not

        self.toggle_labels_button = tk.Button(root, text="Toggle Labels", font=("Arial", 12), command=self.toggle_labels)
        self.toggle_labels_button.pack()

        self.label_button = tk.Button(root, text="Label Points", font=("Arial", 12), command=self.label_points)
        self.label_button.pack()

        self.clear_button = tk.Button(root, text="Clear Paths", font=("Arial", 12), command=self.clear_paths)
        self.clear_button.pack()

        self.simple_path_button = tk.Button(root, text="Simple Path", font=("Arial", 12), command=self.simple_path_algorithm)
        self.simple_path_button.pack()

        self.reset_button = tk.Button(root, text="Reset", font=("Arial", 12), command=self.reset_all)
        self.reset_button.pack()

        self.save_button = tk.Button(root, text="Save Path", font=("Arial", 12), command=self.save_path)
        self.save_button.pack()

        self.calculate_button = tk.Button(root, text="Calculate Optimal Path", font=("Arial", 12), command=self.calculate_optimal_path)
        self.calculate_button.pack()

        # Bind left-click and right-click events
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)\
        
    from itertools import combinations

    def calculate_optimal_path(self):
        """ Calculates the optimal path using BFS with pruning based on subset optimality """

        # Dictionary to store the best distances for subsets of points (both direct and reverse)
        subset_min_distances = {}

        # Action counter
        total_actions = 0

        # BFS queue: each entry will be a tuple of (current_path, remaining_points, current_distance)
        queue = [([self.start_point], set(self.points) - {self.start_point, self.end_point}, 0)]

        while queue:
            # Pop the first path from the queue (FIFO for BFS)
            current_path, remaining_points, current_distance = queue.pop(0)
            total_actions += 1  # Increment action count for each path expansion

            # If no remaining points, calculate the final distance to the end point
            if not remaining_points:
                final_distance = current_distance + self.manhattan_distance(current_path[-1], self.end_point)
                self.clear_paths()  # Clear any existing paths
                for i in range(len(current_path) - 1):
                    self.draw_box(current_path[i], current_path[i + 1])
                self.draw_box(current_path[-1], self.end_point)  # Draw final connection to end point
                print(f"Optimal Path Found with Distance: {final_distance}")
                print(f"Total actions: {total_actions}")
                return  # Exit as soon as we find the optimal path

            # Only generate and compare subsets when there are at least 4 points in the path
            if len(current_path) >= 4:
                # Generate subsets of the current path (same start and end, size >= 4)
                for i in range(1, len(current_path) - 2):  # Ignore the start and end points
                    for j in range(i + 3, len(current_path) + 1):
                        subset = current_path[i:j]

                        # Get Manhattan distance for both direct and reverse order
                        direct_distance = sum(self.manhattan_distance(subset[k], subset[k + 1]) for k in range(len(subset) - 1))
                        reverse_subset = subset[::-1]
                        reverse_distance = sum(self.manhattan_distance(reverse_subset[k], reverse_subset[k + 1]) for k in range(len(reverse_subset) - 1))

                        # Check the best distance for this subset
                        subset_key = tuple(subset)
                        if subset_key in subset_min_distances:
                            best_subset_distance = subset_min_distances[subset_key]
                        else:
                            best_subset_distance = min(direct_distance, reverse_distance)
                            subset_min_distances[subset_key] = best_subset_distance

                        # If the current path has a worse subset distance, prune it
                        if min(direct_distance, reverse_distance) > best_subset_distance:
                            # Prune the path
                            break
                else:
                    # If no pruning happened, continue expanding the path
                    for next_point in remaining_points:
                        if self.valid_path(current_path[-1], next_point, remaining_points):
                            new_distance = current_distance + self.manhattan_distance(current_path[-1], next_point)
                            queue.append((current_path + [next_point], remaining_points - {next_point}, new_distance))
            else:
                # If fewer than 4 points, just continue expanding the path without subset pruning
                for next_point in remaining_points:
                    if self.valid_path(current_path[-1], next_point, remaining_points):
                        new_distance = current_distance + self.manhattan_distance(current_path[-1], next_point)
                        queue.append((current_path + [next_point], remaining_points - {next_point}, new_distance))

        # If the loop finishes without finding an optimal path, print this message
        print("No valid path found.")
        print(f"Total actions: {total_actions}")
    
    def valid_path(self, from_point, to_point, remaining_points):
        """ Check if the connection from from_point to to_point is valid (not shielded by unvisited points) """
        x1, y1 = from_point
        x2, y2 = to_point
        for point in remaining_points:
            px, py = point
            if min(x1, x2) < px < max(x1, x2) and min(y1, y2) < py < max(y1, y2):
                return False  # Shielded, so not a valid path
        return True
    def simple_path_algorithm(self):
        """ Simple path selection algorithm based on pairwise comparison of valid points """
        
        # Reset the paths
        self.clear_paths()
        
        # Start the path with the start point
        current_path = [self.start_point]
        remaining_points = set(self.points) - {self.start_point, self.end_point}

        while remaining_points:
            # Exclude the current point from the remaining points when calculating leftmost/lowest
            remaining_points_excluding_current = remaining_points - {current_path[-1]}

            if len(remaining_points_excluding_current) == 1:
                # If only one point is left, move directly to that point
                best_point = next(iter(remaining_points_excluding_current))
            else:
                best_point = None
                best_score = float("inf")

                # Find the leftmost and lowest remaining points
                leftmost_point = min(remaining_points_excluding_current, key=lambda p: p[0])  # Point with smallest x
                lowest_point = max(remaining_points_excluding_current, key=lambda p: p[1])    # Point with largest y (lowest visually)

                # Compare pairs of valid points
                valid_points = [p for p in remaining_points_excluding_current if self.valid_path(current_path[-1], p, remaining_points)]

                for i in range(len(valid_points)):
                    for j in range(i + 1, len(valid_points)):
                        point1 = valid_points[i]
                        point2 = valid_points[j]

                        # Identify which is higher and which is lower
                        if point1[1] < point2[1]:  # point1 is higher, point2 is lower
                            higher_point = point1
                            lower_point = point2
                        else:  # point2 is higher, point1 is lower
                            higher_point = point2
                            lower_point = point1

                        # Calculate scores
                        higher_point_score = higher_point[1] - lowest_point[1]  # y_higher - y_lowest
                        lower_point_score = lower_point[0] - leftmost_point[0]  # x_lower - x_leftmost

                        # Choose the point with the lower score
                        if higher_point_score < lower_point_score:
                            score = higher_point_score
                            candidate_point = higher_point
                        else:
                            score = lower_point_score
                            candidate_point = lower_point

                        # If the candidate point has a better score, select it
                        if score < best_score:
                            best_score = score
                            best_point = candidate_point

            # Move to the best point
            if best_point:
                self.draw_box(current_path[-1], best_point)
                current_path.append(best_point)
                remaining_points.remove(best_point)
            else:
                print("No valid path found.")
                return

        # Finally, connect to the end point
        self.draw_box(current_path[-1], self.end_point)
        print("Simple path completed.")

    def toggle_labels(self):
        """ Toggle the visibility of the labels for all points """
        
        if self.labels_visible:
            # If labels are visible, remove them
            self.canvas.delete("point_label")
            self.labels_visible = False
        else:
            # If labels are not visible, display them
            for i, point in enumerate(self.points):
                x, y = point
                self.canvas.create_text(x, y+10, text=f"({x}, {y})", font=("Arial", 10), tags="point_label")
            self.labels_visible = True



    def generate_points(self):
        # Get the number of points from the input box
        try:
            num_points = int(self.point_input.get())
            if num_points < 2:
                raise ValueError("Number of points must be at least 2.")
        except ValueError:
            self.show_error_popup("Please enter a valid number of points (2 or more).")
            return
        
        # Reset canvas and points
        self.points = []
        self.paths = []
        self.canvas.delete("all")
        
        # Add start and end points
        self.start_point = (550, 550)  # Bottom left
        self.end_point = (550, 50)     # Top right
        self.points.append(self.start_point)
        self.points.append(self.end_point)
        self.canvas.create_oval(545, 545, 555, 555, fill="red")  # Start point
        self.canvas.create_oval(545, 45, 555, 55, fill="green")  # End point

        # Generate random points (excluding start and end points)
        for _ in range(num_points - 2):
            x = random.randint(100, 500)
            y = random.randint(100, 500)
            point = (x, y)
            self.points.append(point)
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="black")
        
        # Reset distance
        self.total_distance = 0
        self.update_total_distance_label()

    def label_points(self):
        for i, point in enumerate(self.points):
            x, y = point
            self.canvas.create_text(x + 10, y, text=str(i + 1), font=("Arial", 10))

    def on_left_click(self, event):
        click_x, click_y = event.x, event.y
        clicked_point = self.find_closest_point(click_x, click_y)

        if clicked_point is None:
            return
        
        if self.current_point is None:
            self.current_point = clicked_point
        else:
            self.draw_box(self.current_point, clicked_point)
            self.current_point = None

    def draw_box(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        # Draw the rectangular box (Manhattan path)
        horizontal_line = self.canvas.create_line(x1, y1, x2, y1, fill="blue", width=2)  # horizontal line
        vertical_line = self.canvas.create_line(x2, y1, x2, y2, fill="blue", width=2)  # vertical line

        # Add the path to the list (path includes references to the drawn lines)
        self.paths.append((point1, point2, horizontal_line, vertical_line))

        # Calculate Manhattan distance and update total
        distance = abs(x1 - x2) + abs(y1 - y2)
        self.total_distance += distance
        self.update_total_distance_label()

    def find_closest_point(self, x, y):
        for point in self.points:
            px, py = point
            if math.hypot(x - px, y - py) < 10:  # If click is close to a point
                return point
        return None

    def on_right_click(self, event):
        click_x, click_y = event.x, event.y
        clicked_point = self.find_closest_point(click_x, click_y)

        # Check if clicked on a point
        if clicked_point:
            # Show point information including coordinates
            info = self.get_point_info(clicked_point)
            self.show_info_popup(info, event)
        else:
            # Check if clicked on a path and delete it
            self.delete_path_at_click(click_x, click_y)

    def get_point_info(self, point):
        x, y = point
        distance_from_end = 0 if self.end_point is None else self.manhattan_distance(point, self.end_point)
        distance_from_current = 0 if self.current_point is None else self.manhattan_distance(point, self.current_point)
        distance_to_closest_path = self.distance_to_closest_path(point)
        return {
            "X Coordinate": x,
            "Y Coordinate": y,
            "Distance from End": distance_from_end,
            "Distance from Current": distance_from_current,
            "Distance to Closest Path": distance_to_closest_path,
            "Difference (Current - End)": distance_from_current - distance_from_end
        }

    def show_info_popup(self, info, event):
        popup = tk.Toplevel(self.root)
        popup.title("Point Info")
        popup.geometry(f"+{event.x_root}+{event.y_root}")
        for key, value in info.items():
            label = tk.Label(popup, text=f"{key}: {value}")
            label.pack()

    def manhattan_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return abs(x1 - x2) + abs(y1 - y2)

    def distance_to_closest_path(self, point):
        if not self.paths:
            return float("inf")
        min_distance = float("inf")
        for (p1, p2, _, _) in self.paths:
            distance = min(self.manhattan_distance(point, p1), self.manhattan_distance(point, p2))
            if distance < min_distance:
                min_distance = distance
        return min_distance

    def update_total_distance_label(self):
        self.total_distance_label.config(text=f"Total Distance: {self.total_distance}")

    def delete_path_at_click(self, x, y):
        """ Check if right-click occurred near any path, and if so, delete it. """
        for path in self.paths:
            point1, point2, line1, line2 = path
            if self.is_click_near_line(x, y, point1, point2):
                # Delete both lines and remove the path from the list
                self.canvas.delete(line1)
                self.canvas.delete(line2)
                self.paths.remove(path)
                
                # Recalculate total distance after deletion
                distance = self.manhattan_distance(point1, point2)
                self.total_distance -= distance
                self.update_total_distance_label()
                return

    def is_click_near_line(self, x, y, point1, point2):
        """ Check if the click is near the Manhattan box-shaped path between two points. """
        x1, y1 = point1
        x2, y2 = point2
        # Check horizontal line proximity
        if y1 - 5 <= y <= y1 + 5 and min(x1, x2) <= x <= max(x1, x2):
            return True
        # Check vertical line proximity
        if x2 - 5 <= x <= x2 + 5 and min(y1, y2) <= y <= max(y1, y2):
            return True
        return False

    def clear_paths(self):
        """ Clear all paths from the canvas and reset the path list and distance. """
        for _, _, line1, line2 in self.paths:
            self.canvas.delete(line1)
            self.canvas.delete(line2)
        self.paths = []
        self.total_distance = 0
        self.update_total_distance_label()

    def reset_all(self):
        """ Reset the entire canvas, clearing points and paths. """
        self.points = []
        self.paths = []
        self.canvas.delete("all")
        self.total_distance = 0
        self.update_total_distance_label()

    def save_path(self):
        if not self.paths:
            return
        path_info = [f"Path {i+1}: {p1} -> {p2}" for i, (p1, p2, _, _) in enumerate(self.paths)]
        total_info = f"Total Path Length: {self.total_distance}"
        with open("saved_path.txt", "w") as f:
            f.write("\n".join(path_info))
            f.write("\n" + total_info)
        print("Path saved to saved_path.txt")

    def show_error_popup(self, message):
        popup = tk.Toplevel(self.root)
        popup.title("Error")
        tk.Label(popup, text=message).pack()
        tk.Button(popup, text="OK", command=popup.destroy).pack()

    # New crosshair feature
    def update_crosshair(self, event):
        self.canvas.delete("crosshair")
        self.canvas.create_line(0, event.y, 600, event.y, fill="gray", dash=(2, 2), tags="crosshair")
        self.canvas.create_line(event.x, 0, event.x, 600, fill="gray", dash=(2, 2), tags="crosshair")

    def calculate_optimal_path(self):
        """ Calculates the optimal path using pruning and ensuring all points are visited """
        
        # Dictionary to store the shortest distance to a subset of points
        min_distance_to_subset = {}
        
        # Action counter
        path_count = 0
        prune_count = 0
       
        # Recursive function to find the optimal path with pruning
        def find_optimal_path(current_path, remaining_points, current_distance):
            nonlocal path_count, prune_count

            # If no remaining points, calculate the final distance to the end point
            if not remaining_points:
                final_distance = current_distance + self.manhattan_distance(current_path[-1], self.end_point)
                return current_path + [self.end_point], final_distance

            # Prune the path if a shorter distance to the same set of visited points exists
            visited_key = (current_path[-1], frozenset(current_path))
            if visited_key in min_distance_to_subset and min_distance_to_subset[visited_key] <= current_distance:
                prune_count += 1  # Increment prune count
                return None, float("inf")

            # Update the minimum distance to the current subset of visited points
            min_distance_to_subset[visited_key] = current_distance

            # Explore all remaining points
            optimal_subpath = None
            optimal_subdistance = float("inf")
            for next_point in remaining_points:
                path_count += 1  # Increment path action count

                # Check if the path to the next point is valid
                if self.valid_path(current_path[-1], next_point, remaining_points):
                    # Explore this path recursively
                    new_remaining_points = remaining_points - {next_point}
                    new_distance = current_distance + self.manhattan_distance(current_path[-1], next_point)
                    subpath, subdistance = find_optimal_path(current_path + [next_point], new_remaining_points, new_distance)

                    # If the subpath is valid and shorter, update the optimal path
                    if subdistance < optimal_subdistance:
                        optimal_subpath = subpath
                        optimal_subdistance = subdistance

            return optimal_subpath, optimal_subdistance

        # Initialize the search from the start point
        remaining_points = set(self.points) - {self.start_point, self.end_point}
        optimal_path, optimal_distance = find_optimal_path([self.start_point], remaining_points, 0)

        # After search is complete, draw the optimal path if found
        if optimal_path:
            self.clear_paths()  # Clear any existing paths
            for i in range(len(optimal_path) - 1):
                self.draw_box(optimal_path[i], optimal_path[i + 1])
            print(f"Optimal Path Found with Distance: {optimal_distance}")
            print(f"Total number of paths checked: {path_count}")
            print(f"Total number of paths pruned: {prune_count}")
        else:
            print("No valid path found.")

   

if __name__ == "__main__":
    root = tk.Tk()
    app = TSPPApp(root)
    root.mainloop()
