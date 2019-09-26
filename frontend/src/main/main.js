import React from 'react';
import PropTypes from 'prop-types';

import { getCookie } from '../common'
import './main.css';



/**
 * Controls and settings components for the visualization
 */
class Controls extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            show_names: false,
        };
    }

    toggle_checkbox() {
        this.setState({
            show_names: !this.state.show_names,
        });
    }

    render() {
        return (
            <div className="col-3">
                <input
                    type="checkbox"
                    checked={this.state.show_names}
                    onChange={() => this.toggle_checkbox()}
                />
                <label>Show names</label>
            </div>
        );
    }
}

/**
 * The Visualization Itself!
 */
class Viz extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        };
    }

    render() {
        return (
            <div className="col-6">Hello, Sailor!</div>
        );
    }
}

/**
 * Info panel - data from the visualization
 */
class Info extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        };
    }

    render() {
        return (
            <div className="col-3">You clicked on {this.props.name}!</div>
        );
    }
}
Info.propTypes ={
    name: PropTypes.string,
}

/**
 * Main component for the main view.
 */
class MainView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        };
        this.csrftoken = getCookie('csrftoken');
    }

    render() {
        return (
            <div className="container">
                <div className="row">
                    <Controls />
                    <Viz />
                    <Info name='NOTHING YET'/>
                </div>
            </div>
        );
    }
}

export default MainView;
