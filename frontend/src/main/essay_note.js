import React from 'react';

import PropTypes from 'prop-types';

export class EssaySideNote extends React.Component {
    // constructor(props) {
    //     super();
    // }

    render(){
        let sidenote_content;
        if (this.props.url){
            sidenote_content =
                <span className="sidenote">
                    <a href={this.props.url}>{this.props.content}</a>
                </span>;
        } else {
            sidenote_content = <span className="sidenote">{this.props.content}</span>;
        }
        return(
            <>
                <label htmlFor="sn-extensive-use-of-sidenotes"
                    className="margin-toggle sidenote-number"></label>&nbsp;
                <input type="checkbox" id="sn-extensive-use-of-sidenotes"
                    className="margin-toggle"/>
                {sidenote_content}
            </>
        )
    }
}
EssaySideNote.propTypes = {
    content: PropTypes.string.isRequired,
    url: PropTypes.string
};


export default EssaySideNote;
