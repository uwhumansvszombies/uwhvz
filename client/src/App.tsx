import * as React from 'react';
import './App.css';
import './models';
import * as WebRequest from 'web-request';

import AppHeader from './AppHeader';
import User from './models';

interface MyComponentProps { /* declare your component's props here */ }

// Component<Props, State>
export default class App extends React.Component<MyComponentProps, User> {
  constructor(props: MyComponentProps) {
    super(props);
    this.state = new User('', '', '', '');
  }

  componentDidMount() {
    WebRequest.json<User>('http://localhost:8000').then(res => {
      this.setState(res);
    }).catch(res => {
      this.setState(new User('', '', '', ''));
    });
  }

  render() {
    return (
      <div>
        <AppHeader>test</AppHeader>
        <div className="main">
          <p>{this.state.email}</p>
          <p>{this.state.firstName}</p>
          <p>{this.state.lastName}</p>
          <p>{this.state.username}</p>
        </div>
      </div>
    );
  }
}
