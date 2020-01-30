import React from 'react';
import PropTypes from 'prop-types';

import './main_layout.css'



class NavigationBar extends React.Component {

    render() {

        return (
            <nav className="navbar navbar-expand-sm navbar-dark bg-dark">
                <a className="navbar-brand nav-item" href="/">Tobacco Networks</a>
                <button className="navbar-toggler" type="button" data-toggle="collapse"
                    data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup"
                    aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
                    <div className='navbar-nav'>
                        <a className="nav-item nav-link active" href="/explore_networks/">
                            Explore Industry Networks</a>
                        <a className="nav-item nav-link active" href="/research_directors/">
                            Research Directors</a>
                        <a className="nav-item nav-link active" href="/sterling/">
                            Theodor Sterling</a>
                        <a className="nav-item nav-link active" href="/about/">
                            About</a>
                    </div>
                </div>
            </nav>
        );
    }
}

class Footer extends React.Component {
    render() {
        return (
            <footer className="footer bg-white text-dark text-center mt-auto">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-4 py-3">
                            <a href="https://digitalhumanities.mit.edu/">
                                <img
                                    src="/static/img/nav/dh_logo.png"
                                    className='footer-img'
                                    alt='Digital Humanities at MIT Logo'
                                />
                            </a>
                        </div>
                        <div className="col-4 py-3">
                            <a href="https://www.mit.edu/">
                                <img
                                    src="/static/img/nav/mit_logo.svg"
                                    className='footer-img'
                                    alt='MIT Logo'
                                />
                            </a>
                        </div>
                        <div className="col-4 py-3">
                            <a href="https://www.mellon.org/">
                                <img
                                    src="/static/img/nav/mellon_logo.svg"
                                    className='footer-img'
                                    alt="Mellon Foundation Logo"
                                />
                            </a>
                        </div>
                    </div>
                </div>
            </footer>
        );
    }
}


export class MainLayout extends React.Component {
    render() {
        return (
            <>
                <NavigationBar/>
                <div className='container' id="main_content_container">
                    {this.props.content}
                </div>
                <Footer/>
            </>
        )
    }
}

MainLayout.propTypes = {
    content: PropTypes.node
};

export default MainLayout;
