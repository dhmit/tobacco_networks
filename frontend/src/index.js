import React from 'react';
import ReactDOM from 'react-dom';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';  // JS import -- just for collapse

import MainView from './main/main';

import NetworkExplorationView from "./main/network_exploration";
import SterlingEssayView from "./main/essay_sterling";
import ResearchDirectorsEssayView from "./main/essay_research_directors";
import TeamView from "./main/team";

window.app_modules = {
    React,  // Make React accessible from the base template
    ReactDOM,  // Make ReactDOM accessible from the base template

    // Add all frontend views here

    NetworkExplorationView,

    SterlingEssayView,
    ResearchDirectorsEssayView,
    TeamView,
    MainView,
};
