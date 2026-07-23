using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc.Testing;

namespace AgentBattleArena.Live.Api.Tests;

public class HealthEndpointTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public HealthEndpointTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task Health_returns_ok_for_live_mode()
    {
        var response = await _client.GetAsync("/api/v1/live/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var payload = await response.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("ok", payload.GetProperty("status").GetString());
        Assert.Equal("live-3d", payload.GetProperty("mode").GetString());
        Assert.Equal("AgentBattleArena.Live.Api", payload.GetProperty("service").GetString());
    }
}
