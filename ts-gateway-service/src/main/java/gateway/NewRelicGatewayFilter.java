package gateway;

import com.newrelic.api.agent.NewRelic;
import com.newrelic.api.agent.Trace;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.cloud.gateway.route.Route;
import org.springframework.core.Ordered;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import static org.springframework.cloud.gateway.support.ServerWebExchangeUtils.GATEWAY_ROUTE_ATTR;

/**
 * New Relic Gateway Filter for tracking gateway metrics and distributed tracing
 *
 * @author New Relic Integration
 */
@Component
public class NewRelicGatewayFilter implements GlobalFilter, Ordered {

    @Override
    @Trace
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        long startTime = System.currentTimeMillis();

        // Get route information
        Route route = exchange.getAttribute(GATEWAY_ROUTE_ATTR);
        String routeId = route != null ? route.getId() : "unknown";
        String path = exchange.getRequest().getPath().value();
        String method = exchange.getRequest().getMethod().name();

        // Add custom attributes for New Relic (handled at runtime)
        try {
            NewRelic.recordMetric("Custom/Gateway/Requests/Total", 1);
            NewRelic.recordMetric("Custom/Gateway/Routes/" + routeId + "/Count", 1);
        } catch (NoClassDefFoundError | Exception e) {
            // New Relic agent not available at compile time, will be available at runtime
        }

        return chain.filter(exchange)
            .doOnSuccess(unused -> {
                // Track successful requests
                long duration = System.currentTimeMillis() - startTime;
                try {
                    NewRelic.recordMetric("Custom/Gateway/Requests/Success", 1);
                    NewRelic.recordMetric("Custom/Gateway/Routes/" + routeId + "/Duration", duration);
                } catch (NoClassDefFoundError | Exception e) {
                    // New Relic agent not available at compile time
                }
            })
            .doOnError(error -> {
                // Track failed requests
                try {
                    NewRelic.recordMetric("Custom/Gateway/Requests/Error", 1);
                    NewRelic.noticeError(error);
                } catch (NoClassDefFoundError | Exception e) {
                    // New Relic agent not available at compile time
                }
            });
    }

    @Override
    public int getOrder() {
        // Run before Sentinel filter (which has order -1)
        return -10;
    }
}