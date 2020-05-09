-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 09, 2020 at 12:41 AM
-- Server version: 5.7.24
-- PHP Version: 7.2.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `natural_cure`
--

-- --------------------------------------------------------

--
-- Table structure for table `treatment`
--

DROP TABLE IF EXISTS `treatment`;
CREATE TABLE IF NOT EXISTS `treatment` (
  `illness` varchar(128) NOT NULL,
  `remedy` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`illness`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `treatment`
--

INSERT INTO `treatment` (`illness`, `remedy`) VALUES
('Hypothyroidism', 'Try adding Selenium to your diet through:tuna,turkey,Brazil nuts,grass-fed beef;Start a sugar-free diet;Improve vitamin B levels by including the following foods in your diet:peas and beans,asparagus,sesame seeds,tuna,cheese,milk,eggs;Consume fermented foods and drinks which contain probiotics:kefir,kombucha,yogurt; Adopt a gluten-free diet'),
('Mechanical back pain', 'Enjoy an anti-inflammatory drink every day:Turmeric milk,Tart cherry juice,Ginger-green tea;Fall asleep faster and sleep longer;Avoid prolonged static posture:Avoid excessive sitting,Check your posture and adjust your back alignment to prevent stresses on your spine,Rotate activities to avoid muscle and joint over-fatigue;Gently stretch your joints and soft tissues through yoga;Try mindful meditation;Keep a heat patch handy;Try the following herbs:Devil’s claw (50 or 100 mg daily),Willow bark(120 or 240 mg daily);Take a relaxing Epsom salt bath'),
('Migraine', 'Apply lavender oil;Try acupressure;Look for feverfew (a flowering herb that looks like a daisy);Apply peppermint oil;Go for ginger;Sign up for yoga;Try biofeedback (a relaxation method which teaches you to control autonomic reactions to stress);Add magnesium to your diet from foods like:almonds,sesame seeds,sunflower seeds,Brazil nuts,cashews,peanut butter,oatmeal,eggs,milk;Book a massage'),
('General anxiety disorder', 'Stay active;Don’t drink alcohol;Stop smoking;Ditch caffeine;Get some good sleep;Meditate;Eat a healthy diet and avoid processed food;Stay hydrated;Practice deep breathing;Drink chamomile tea;Try aromatherapy'),
('Joint pain, unspecified', 'Lose weight;Get more exercise;Use hot and cold therapy;Try acupuncture;Use meditation to cope with pain;Include more omega-3 fatty acids in your diet from:Mackerel (4107 mg per serving),Salmon (4123 mg per serving),Cod liver oil (2682 mg per serving),Herring (946 mg per serving),Sardines (2205 mg per serving),Flax seeds (2350 mg per serving),Chia seeds (5060 mg per serving),Walnuts (2570 mg per serving);Add more gamma-linolenic acid, or GLA, to your diet from the seeds of certain plants such as:evening primrose,borage,hemp,black currants;Add turmeric to dishes;Get a massage;Consider these herbal supplements:boswellia,bromelain,devil’s claw,ginkgo,stinging nettle'),
('Abdominal pain, unspecified', 'Make a Drink with Apple Cider Vinegar;Try Some Ginger;Soothe Your Stomach with Fennel;Brew Some Chamomile Tea;Sip some Club Soda;Drink Warm Salt Water;Brew some Cinnamon Tea;Drink Lemon Tea;Do some Gentle Yoga Stretches');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
