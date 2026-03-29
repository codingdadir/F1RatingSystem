# F1 Driver Rating System

A data science project by Abdulkadir Abdalla

## Project Summary

This project builds a custom driver rating system for Formula 1, designed to evaluate driver performance more fairly and accurately than championship points alone.

Championship points are heavily influenced by the car — a driver in a dominant car will score points almost regardless of their individual performance, while a driver in a backmarker car may drive brilliantly and score nothing. This system attempts to strip away the car's influence and rate drivers on what they actually control: how well they qualify relative to their teammate, how much they gain or lose positions in the race, and how often they make mistakes that end their race.

The rating is built on four components — qualifying performance vs teammate, race finish vs teammate, positions gained or lost, and a DNF penalty that distinguishes between driver errors and mechanical failures. Each component is normalised and weighted, then fed into an ELO-style system that tracks driver ratings across every race from 2006 to 2025. Constructor championship standings are used to provide season context, so a strong result in a backmarker car is valued more highly than the same result in a dominant car.

The project is end-to-end: a Python pipeline fetches data from the Jolpica F1 API, stores it in a structured SQLite database, runs the rating model, and presents the results in an interactive Streamlit dashboard.