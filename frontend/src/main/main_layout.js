import React from 'react';
import PropTypes from 'prop-types';



class NavigationBar extends React.Component {

    render() {

        return (
            <nav className="navbar navbar-expand-sm navbar-dark bg-dark">
                <a className="navbar-brand" href="#">Tobacco Networks</a>
                <button className="navbar-toggler" type="button" data-toggle="collapse"
                    data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup"
                    aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
                    <div className='navbar-nav'>
                        <a className="nav-item nav-link active" href="#">Research Directors</a>
                        <a className="nav-item nav-link active" href="#">Lawyers</a>
                    </div>
                </div>
            </nav>
        );
    }
}

export class MainLayout extends React.Component {
    render() {
        return (
            <>
                <NavigationBar/>
                <div className='container'>
                    {this.props.content}
                </div>
            </>
        )
    }
}

MainLayout.propTypes = {
    content: PropTypes.node
};

export default MainLayout;
