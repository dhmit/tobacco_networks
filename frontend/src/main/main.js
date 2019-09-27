/**
 * UI Code for the visualization
 */
import React from 'react';
import PropTypes from 'prop-types';

import { getCookie } from '../common'
import { create_graph, update_graph } from './graph.js'
import './main.css';


/***************************************************************************************************
 * Controls and settings components for the visualization
 **************************************************************************************************/
class Controls extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const checked = this.props.config.color === 'blue';
        return (
            <div className="col-3">
                <input
                    type="checkbox"
                    checked={checked}
                    onChange={this.props.handle_checkbox}
                />
                <label>Color is blue</label>
            </div>
        );
    }
}
Controls.propTypes = {
    config: PropTypes.object,
    handle_checkbox: PropTypes.func.isRequired,
};

/***************************************************************************************************
 * Wrapper for the Visualization
 **************************************************************************************************/
class Viz extends React.Component {
    constructor(props) {
        super(props);
        this._graphRoot = React.createRef();
    }

    componentDidMount() {
        // D3 Code to create the chart
        this._graph = create_graph(
            this._graphRoot.current,
            this.props.data,
            this.props.config,
            this.props.handle_viz_events,
        );
    }

    componentDidUpdate() {
        // D3 Code to update the chart
        update_graph(
            this._graphRoot.current,
            this.props.data,
            this.props.config,
            this._graph,
        );
    }

    componentWillUnmount() {
        // TobaccoNetworkGraph.destroy(this._graphRoot);
    }

    render() {
        return (
            <div className="col-6" ref={this._graphRoot}>

            </div>
        )
    }
}
Viz.propTypes = {
    data: PropTypes.object.isRequired,
    config: PropTypes.object.isRequired,
    handle_viz_events: PropTypes.func,
};

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
            <div className="col-3">
                Your mouse is {this.props.mouseover ? 'OVER' : 'NOT OVER'}  a bar on the viz!
            </div>
        );
    }
}
Info.propTypes ={
    mouseover: PropTypes.bool,
};

/***************************************************************************************************
 * Main component for the main view.
 **************************************************************************************************/
class MainView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            config: null,
            data: null,
            mouseover: false,
        };
        this.csrftoken = getCookie('csrftoken');
    }

    componentDidMount() {
        // TODO(ra): ask the server for some data
        const config = {
            width: 500,
            height: 500,
            color: 'blue',
        };
        const data = {
            values: [4,5,6,7],
        };
        this.setState({
            config: config,
            data: data,
        });
    }

    handle_checkbox() {
        const config = {...this.state.config};
        if (config.color === 'blue') {
            config.color = 'red';
        } else {
            config.color = 'blue'
        }
        this.setState({
            config: config,
        })
    }

    handle_viz_events(event_name) {
        if (event_name === "mouseover") {
            this.setState({mouseover: true});
        } else if (event_name === "mouseout") {
            this.setState({mouseover: false});
        }
    }

    render() {
        if (this.state.data) {
            return (
                <div className="container">
                    <div className="row">
                        <Controls
                            handle_checkbox={() => this.handle_checkbox()}
                            config={this.state.config}
                        />
                        <Viz
                            data={this.state.data}
                            config={this.state.config}
                            handle_viz_events={(event_name) => this.handle_viz_events(event_name)}
                        />
                        <Info
                            mouseover={this.state.mouseover}
                        />
                    </div>
                </div>
            );
        } else {
            return (
                <div>Loading!</div>
            )
        }
    }
}

export default MainView;
