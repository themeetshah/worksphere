-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 11, 2025 at 08:27 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `worksphere`
--

-- --------------------------------------------------------

--
-- Table structure for table `expenses`
--

CREATE TABLE `expenses` (
  `expense_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `date` date NOT NULL DEFAULT current_timestamp(),
  `approved` enum('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (`expense_id`, `project_id`, `user_id`, `amount`, `category`, `description`, `date`, `approved`) VALUES
(1, 1, 6, 15000.00, 'Software Licenses', 'UI/UX tools', '2025-02-25', 'Pending'),
(2, 1, 4, 25000.00, 'Equipment', 'Servers', '2025-02-20', 'Approved'),
(3, 2, 7, 10000.00, 'Marketing', 'Google Ads', '2025-02-15', 'Rejected'),
(4, 2, 7, 8000.00, 'Marketing', 'Youtube Ads', '2025-02-20', 'Approved'),
(5, 5, 16, 1200.00, 'Software Price', 'abc', '2025-03-12', 'Approved'),
(6, 5, 6, 1000.00, 'Clash', 'bca', '2025-03-12', 'Rejected');

-- --------------------------------------------------------

--
-- Table structure for table `polls`
--

CREATE TABLE `polls` (
  `poll_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `question` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `closes_at` datetime NOT NULL,
  `is_closed` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `polls`
--

INSERT INTO `polls` (`poll_id`, `project_id`, `created_by`, `question`, `created_at`, `closes_at`, `is_closed`) VALUES
(1, 1, 4, 'Which frontend framework should we use?', '2025-02-20 10:00:00', '2025-02-22 23:59:59', 1),
(2, 2, 5, 'Should we focus more on SEO or paid ads?', '2025-02-18 15:00:00', '2025-02-21 23:59:59', 1),
(5, 5, 16, 'Is this appropriate?', '2025-03-12 00:45:43', '2025-03-12 00:50:00', 1);

-- --------------------------------------------------------

--
-- Table structure for table `poll_options`
--

CREATE TABLE `poll_options` (
  `option_id` int(11) NOT NULL,
  `poll_id` int(11) NOT NULL,
  `option_text` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `poll_options`
--

INSERT INTO `poll_options` (`option_id`, `poll_id`, `option_text`) VALUES
(1, 1, 'React.js'),
(2, 1, 'Vue.js'),
(3, 1, 'Angular'),
(4, 2, 'SEO Optimization'),
(5, 2, 'Paid Ads'),
(10, 5, 'Yes'),
(11, 5, 'No'),
(12, 5, 'idk');

-- --------------------------------------------------------

--
-- Table structure for table `poll_votes`
--

CREATE TABLE `poll_votes` (
  `vote_id` int(11) NOT NULL,
  `poll_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `option_id` int(11) NOT NULL,
  `voted_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `poll_votes`
--

INSERT INTO `poll_votes` (`vote_id`, `poll_id`, `user_id`, `option_id`, `voted_at`) VALUES
(1, 1, 6, 1, '2025-02-21 12:00:00'),
(2, 1, 4, 2, '2025-02-21 13:30:00'),
(3, 2, 5, 4, '2025-02-19 10:45:00'),
(4, 2, 7, 5, '2025-02-19 11:20:00'),
(5, 5, 16, 12, '2025-03-12 00:45:48'),
(6, 5, 6, 10, '2025-03-12 00:48:32');

-- --------------------------------------------------------

--
-- Table structure for table `projects`
--

CREATE TABLE `projects` (
  `project_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `client` varchar(255) DEFAULT NULL,
  `budget` decimal(10,2) DEFAULT NULL,
  `status` enum('Pending','Completed') DEFAULT 'Pending',
  `team_id` int(11) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `projects`
--

INSERT INTO `projects` (`project_id`, `name`, `description`, `client`, `budget`, `status`, `team_id`, `created_by`, `created_at`) VALUES
(1, 'E-Commerce Website', 'Developing an online shopping platform', 'Reliance Digital', 500000.00, 'Completed', 1, 2, '2025-02-26 20:54:56'),
(2, 'Digital Marketing Campaign', 'Social media and SEO marketing for a brand', 'Tata Group', 300000.00, 'Completed', 2, 3, '2025-02-26 20:54:56'),
(5, 'Social Site', 'None', 'Meta', 15000.00, 'Completed', 1, 2, '2025-02-26 21:33:21'),
(6, 'Testing Proj', 'Just Testing', 'LJKU', 1500.00, 'Pending', 1, 2, '2025-03-11 19:21:19');

-- --------------------------------------------------------

--
-- Table structure for table `tasks`
--

CREATE TABLE `tasks` (
  `task_id` int(11) NOT NULL,
  `project_id` int(11) DEFAULT NULL,
  `team_id` int(11) DEFAULT NULL,
  `assigned_to` int(11) DEFAULT NULL,
  `task_name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `deadline` date DEFAULT NULL,
  `submission` date DEFAULT NULL,
  `status` enum('Pending','Completed') DEFAULT 'Pending',
  `submission_file` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tasks`
--

INSERT INTO `tasks` (`task_id`, `project_id`, `team_id`, `assigned_to`, `task_name`, `description`, `deadline`, `submission`, `status`, `submission_file`) VALUES
(1, 1, 1, 6, 'Frontend Design', 'Create UI components', '2025-02-13', '2025-02-25', 'Completed', 'uploads/poll_results.png'),
(2, 1, 1, 4, 'Backend Development', 'Setup APIs and database', '2025-03-10', '2025-02-27', 'Completed', 'uploads/requirements.txt'),
(3, 2, 2, 7, 'SEO Optimization', 'Improve website ranking', '2025-02-20', '2025-02-19', 'Completed', 'uploads/requirements.txt'),
(4, 1, 1, 16, 'Bug Testing', 'Detect & Solve', '2025-02-28', '2025-02-28', 'Completed', 'uploads/requirements.txt'),
(7, 1, 1, 4, 'rsrfvs', 'vsevers', '2025-02-28', '2025-02-15', 'Completed', 'uploads/Chapter_9.pdf'),
(10, 5, 1, 6, 'Task1', 'Do this asap.', '2025-03-20', '2025-03-12', 'Completed', 'uploads/requirements.txt');

-- --------------------------------------------------------

--
-- Table structure for table `teams`
--

CREATE TABLE `teams` (
  `team_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `manager_id` int(11) NOT NULL,
  `leader_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `teams`
--

INSERT INTO `teams` (`team_id`, `name`, `manager_id`, `leader_id`) VALUES
(1, 'Development Team', 2, 16),
(2, 'Marketing Team', 3, 5),
(12, 'Designing Team', 2, 0),
(13, 'Devs 1', 2, 18);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('Owner','Manager','Team Leader','Team Member','Employee') NOT NULL DEFAULT 'Employee',
  `team_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `name`, `email`, `password`, `role`, `team_id`) VALUES
(1, 'Ravi Sharma', 'ravi.sharma@example.com', 'password123', 'Owner', NULL),
(2, 'Priya Verma', 'priya.verma@example.com', 'password123', 'Manager', NULL),
(3, 'Amit Patel', 'amit.patel@example.com', 'password123', 'Manager', NULL),
(4, 'Sneha Iyer', 'sneha.iyer@example.com', 'password123', 'Team Member', 1),
(5, 'Rajesh Gupta', 'rajesh.gupta@example.com', 'password123', 'Team Leader', 2),
(6, 'Kiran Nair', 'kiran.nair@example.com', 'password123', 'Team Member', 1),
(7, 'Sandeep Mehta', 'sandeep.mehta@example.com', 'password123', 'Team Member', 2),
(16, 'Meet Shah', 'meet.shah@example.com', 'pass123', 'Team Leader', 1),
(17, 'M S', 'm.s@example.com', 'pass123', 'Team Member', 1),
(18, 'S M', 's.m@example.com', 'pass123', 'Team Leader', 13);

-- --------------------------------------------------------

--
-- Table structure for table `working_hours`
--

CREATE TABLE `working_hours` (
  `entry_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `hours` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `working_hours`
--

INSERT INTO `working_hours` (`entry_id`, `user_id`, `date`, `hours`) VALUES
(1, 1, '2025-02-28', 6),
(2, 16, '2025-02-28', 7),
(3, 16, '2025-02-18', 5),
(4, 16, '2025-02-07', 3),
(7, 16, '2025-03-11', 6);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `expenses`
--
ALTER TABLE `expenses`
  ADD PRIMARY KEY (`expense_id`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `polls`
--
ALTER TABLE `polls`
  ADD PRIMARY KEY (`poll_id`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `poll_options`
--
ALTER TABLE `poll_options`
  ADD PRIMARY KEY (`option_id`),
  ADD KEY `poll_id` (`poll_id`);

--
-- Indexes for table `poll_votes`
--
ALTER TABLE `poll_votes`
  ADD PRIMARY KEY (`vote_id`),
  ADD KEY `poll_id` (`poll_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `option_id` (`option_id`);

--
-- Indexes for table `projects`
--
ALTER TABLE `projects`
  ADD PRIMARY KEY (`project_id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `tasks`
--
ALTER TABLE `tasks`
  ADD PRIMARY KEY (`task_id`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `assigned_to` (`assigned_to`);

--
-- Indexes for table `teams`
--
ALTER TABLE `teams`
  ADD PRIMARY KEY (`team_id`),
  ADD KEY `manager_id` (`manager_id`),
  ADD KEY `leader_id` (`leader_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `working_hours`
--
ALTER TABLE `working_hours`
  ADD PRIMARY KEY (`entry_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `expenses`
--
ALTER TABLE `expenses`
  MODIFY `expense_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `polls`
--
ALTER TABLE `polls`
  MODIFY `poll_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `poll_options`
--
ALTER TABLE `poll_options`
  MODIFY `option_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `poll_votes`
--
ALTER TABLE `poll_votes`
  MODIFY `vote_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `projects`
--
ALTER TABLE `projects`
  MODIFY `project_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `tasks`
--
ALTER TABLE `tasks`
  MODIFY `task_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `teams`
--
ALTER TABLE `teams`
  MODIFY `team_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `working_hours`
--
ALTER TABLE `working_hours`
  MODIFY `entry_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `expenses`
--
ALTER TABLE `expenses`
  ADD CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_expenses_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `polls`
--
ALTER TABLE `polls`
  ADD CONSTRAINT `polls_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`),
  ADD CONSTRAINT `polls_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `poll_options`
--
ALTER TABLE `poll_options`
  ADD CONSTRAINT `poll_options_ibfk_1` FOREIGN KEY (`poll_id`) REFERENCES `polls` (`poll_id`) ON DELETE CASCADE;

--
-- Constraints for table `poll_votes`
--
ALTER TABLE `poll_votes`
  ADD CONSTRAINT `poll_votes_ibfk_1` FOREIGN KEY (`poll_id`) REFERENCES `polls` (`poll_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `poll_votes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `poll_votes_ibfk_3` FOREIGN KEY (`option_id`) REFERENCES `poll_options` (`option_id`);

--
-- Constraints for table `projects`
--
ALTER TABLE `projects`
  ADD CONSTRAINT `projects_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`team_id`),
  ADD CONSTRAINT `projects_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `tasks`
--
ALTER TABLE `tasks`
  ADD CONSTRAINT `tasks_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`),
  ADD CONSTRAINT `tasks_ibfk_2` FOREIGN KEY (`team_id`) REFERENCES `teams` (`team_id`),
  ADD CONSTRAINT `tasks_ibfk_3` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `teams`
--
ALTER TABLE `teams`
  ADD CONSTRAINT `teams_ibfk_1` FOREIGN KEY (`manager_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
