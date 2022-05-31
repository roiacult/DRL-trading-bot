FROM node:15-alpine

ARG build_type="production"

RUN apk --no-cache add --virtual native-deps \
    g++ gcc libgcc libstdc++ linux-headers make python2 && \
    npm install --quiet node-gyp -g

RUN mkdir -p /opt/rl-trader-front
WORKDIR /opt/rl-trader-front
COPY . .

RUN yarn install
RUN yarn global add serve

# build
RUN yarn build

# RUN chmod u+x entrypoint.sh

RUN export NODE_OPTIONS="--max-old-space-size=8192"

CMD ["serve", "-s", "build"]