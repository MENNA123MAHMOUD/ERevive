mkdir FrontCode
cd ./FrontCode
touch .babelrc.js
touch webpack.config.js
npm init -y

mkdir src
mkdir src/components
mkdir src/store
mkdir src/store/modules
mkdir src/views
mkdir src/router
mkdir src/scss

touch src/main.js
touch src/App.vue
touch src/index.html
cd ./src
npm install axios vue vue-loader vuex vue-router vue-template-compiler webpack webpack-cli webpack-dev-server babel-loader @babel/core @babel/preset-env sass sass-loader css-loader vue-style-loader html-webpack-plugin rimraf -D

cd ../
python3 writeFiles.py
cd ./FrontCode
npm run serve